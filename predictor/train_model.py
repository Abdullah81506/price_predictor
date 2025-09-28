import os
import joblib
import random
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load city JSON
import json
with open(os.path.join(BASE_DIR, "california_cities.json"), "r") as f:
    cities = json.load(f)

# Generate synthetic dataset
data = []
for city in cities:   # e.g., 20 cities
    for _ in range(10):  # 10 houses per city
        size = random.randint(1200, 3500)
        rooms = random.randint(2, 5)
        bathrooms = random.randint(1, 3)
        age = random.randint(1, 30)
        lat = city["lat"]
        lon = city["lon"]

        # price baseline formula + noise
        base_price = (size * 0.2) + (rooms * 30) + (bathrooms * 25) - (age * 2)
        price = base_price + random.uniform(-50, 50)

        data.append({
            "size": size,
            "rooms": rooms,
            "bathrooms": bathrooms,
            "age": age,
            "latitude": lat,
            "longitude": lon,
            "price_in_k": round(price, 2),
        })

df = pd.DataFrame(data)

# Features/target
X = df[['size', 'rooms', 'bathrooms', 'age', 'latitude', 'longitude']]
y = df['price_in_k']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
coefficients = model.coef_
intercept = model.intercept_

print("Model Evaluation")
print(f"MSE: {mse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.2f}")

# Save model
model_path = os.path.join(BASE_DIR, "house_model.pkl")
joblib.dump(model, model_path)
print(f"Saved model to {model_path}")

# Save test results
df_test_original = X_test.copy()
df_test_original["actual_price"] = y_test
df_test_original["predicted_price"] = y_pred
test_results_path = os.path.join(BASE_DIR, "test_results.csv")
df_test_original.to_csv(test_results_path, index=False)
print(f"Saved test results to {test_results_path}")

# Save metrics
feature_names = list(X.columns)
feature_stds = X_train.std(axis=0)
standardized_coefs = coefficients * feature_stds

metrics_dict = {
    "mse": mse,
    "mae": mae,
    "rmse": rmse,
    "r2": r2,
    "intercept": intercept,
}
for name, coef, std_coef in zip(feature_names, coefficients, standardized_coefs):
    metrics_dict[f"coef_{name}"] = coef
    metrics_dict[f"std_coef_{name}"] = std_coef

metrics_path = os.path.join(BASE_DIR, "metrics.csv")
metrics_df = pd.DataFrame([metrics_dict])
metrics_df.to_csv(metrics_path, index=False)
print(f"Saved metrics to {metrics_path}")
