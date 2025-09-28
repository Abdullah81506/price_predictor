import os, joblib, pandas as pd, json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PredictionHistory
from .serializers import PredictionHistorySerializer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, "house_model.pkl"))

# Load cities
CITIES_FILE = os.path.join(BASE_DIR, "california_cities.json")
with open(CITIES_FILE, "r") as f:
    CALIFORNIA_CITIES = json.load(f)

@api_view(["POST"])
def predict_price_api(request):
    """
    API endpoint for price prediction
    """
    try:
        size = int(request.data.get("size"))
        rooms = int(request.data.get("rooms"))
        bathrooms = int(request.data.get("bathrooms"))
        age = int(request.data.get("age"))
        city = request.data.get("city")

        city_data = next((c for c in CALIFORNIA_CITIES if c["city"] == city), None)
        if not city_data:
            return Response({"error": f"City {city} not found"}, status=status.HTTP_400_BAD_REQUEST)

        lat, lon = city_data["lat"], city_data["lon"]

        # Prepare input
        input_final = pd.DataFrame([{
            "size": size,
            "rooms": rooms,
            "bathrooms": bathrooms,
            "age": age,
            "latitude": lat,
            "longitude": lon,
        }])

        prediction = model.predict(input_final)[0]
        prediction = round(prediction, 2)

        # Save history
        record = PredictionHistory.objects.create(
            size=size, rooms=rooms, bathrooms=bathrooms,
            age=age, location=city, latitude=lat, longitude=lon,
            predicted_price=prediction
        )

        return Response({
            "city": city,
            "prediction": prediction,
            "record_id": record.id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def prediction_history_api(request):
    """
    API endpoint to fetch history
    """
    history = PredictionHistory.objects.all().order_by("-created_at")
    serializer = PredictionHistorySerializer(history, many=True)
    return Response(serializer.data)
