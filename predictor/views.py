from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
import joblib
import os
import pandas as pd
from .models import PredictionHistory
from django.views.decorators.http import require_POST
import json

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load trained model
model = joblib.load(os.path.join(BASE_DIR, "house_model.pkl"))

# ------------------ Load California cities from JSON ------------------
CITIES_FILE = os.path.join(BASE_DIR, "california_cities.json")

def load_cities():
    try:
        with open(CITIES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading cities:", e)
        return []

CALIFORNIA_CITIES = load_cities()

# ------------------ Main prediction view ------------------
def predict_price(request):
    if request.method == "POST":
        try:
            size = int(request.POST.get("size"))
            rooms = int(request.POST.get("rooms"))
            bathrooms = int(request.POST.get("bathrooms"))
            age = int(request.POST.get("age"))
            city = request.POST.get("city")

            if not city:
                messages.error(request, "Please select a city.")
                return redirect("predict")

            city_data = next((c for c in CALIFORNIA_CITIES if c["city"] == city), None)
            if not city_data:
                messages.error(request, f"City {city} not found in list.")
                return redirect("predict")

            lat, lon = city_data["lat"], city_data["lon"]

            # Prepare input for model
            input_final = pd.DataFrame([{
                "size": size,
                "rooms": rooms,
                "bathrooms": bathrooms,
                "age": age,
                "latitude": lat,
                "longitude": lon
            }])

            # Predict
            prediction = model.predict(input_final)[0]
            prediction = round(prediction, 2)

            # Save history
            PredictionHistory.objects.create(
                size=size,
                rooms=rooms,
                bathrooms=bathrooms,
                age=age,
                location=city,
                latitude=lat,
                longitude=lon,
                predicted_price=prediction
            )

            messages.success(
                request,
                f"<b>Predicted Price for {city}, CA: ${prediction:,.2f}k</b>"
            )
            return redirect("predict")

        except ValueError as e:
            messages.error(request, f"Invalid input: {e}")
            return redirect("predict")
        except Exception as e:
            messages.error(request, f"Prediction error: {e}")
            return redirect("predict")

    # GET request → show form with cities
    return render(request, "predictor/form.html", {
        "cities": CALIFORNIA_CITIES,
        "selected_region": "California"
    })

# ------------------ Evaluation View ------------------
def evaluate(request):
    results_path = os.path.join(BASE_DIR, "test_results.csv")
    metrics_path = os.path.join(BASE_DIR, "metrics.csv")

    results, mse, r2, mae, rmse, intercept = [], None, None, None, None, None
    coefficients = {}
    actual_prices, predicted_prices = [], []

    if os.path.exists(results_path):
        df = pd.read_csv(results_path)
        results = df.to_dict(orient="records")
        actual_prices = df["actual_price"].tolist()
        predicted_prices = df["predicted_price"].tolist()

    feature_names = []
    importances = []
    if os.path.exists(metrics_path):
        metrics = pd.read_csv(metrics_path).iloc[0]
        mse, r2, mae, rmse = (
            round(metrics["mse"], 2),
            round(metrics["r2"], 2),
            round(metrics["mae"], 2),
            round(metrics["rmse"], 2),
        )
        intercept = round(metrics["intercept"], 2)

        std_coefs = []
        for col in metrics.index:
            if col.startswith("coef_"):
                feat_name = col.replace("coef_", "")
                coef_val = float(metrics[col])
                coefficients[feat_name] = coef_val
                feature_names.append(feat_name)
            elif col.startswith("std_coef_"):
                std_coefs.append(float(metrics[col]))

        importance_vals = [abs(v) for v in std_coefs]
        total = sum(importance_vals) if sum(importance_vals) != 0 else 1
        importances = [(c / total) * 100 for c in importance_vals]

    scatter_points = [{"x": a, "y": p} for a, p in zip(actual_prices, predicted_prices)]

    perfect_fit = []
    if actual_prices:
        min_val, max_val = min(actual_prices), max(actual_prices)
        perfect_fit = [{"x": min_val, "y": min_val}, {"x": max_val, "y": max_val}]

    context = {
        "results": results,
        "mse": mse,
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "intercept": intercept,
        "coefficients": coefficients,
        "feature_names_json": json.dumps(feature_names),
        "importances_json": json.dumps(importances),
        "scatter_points_json": json.dumps(scatter_points),
        "perfect_fit_json": json.dumps(perfect_fit),
    }
    return render(request, "predictor/evaluate.html", context)

# ------------------ History Views ------------------
def prediction_history(request):
    history = PredictionHistory.objects.all().order_by('-created_at')
    return render(request, 'predictor/history.html', {'history': history})

def clear_history(request):
    if request.method == "POST":
        PredictionHistory.objects.all().delete()
        messages.success(request, "Prediction history cleared successfully!")
        return redirect("history")

@require_POST
def delete_history(request, id):
    record = get_object_or_404(PredictionHistory, id=id)
    record.delete()
    messages.success(request, "Record deleted successfully.")
    return redirect("history")
