from rest_framework import serializers
from .models import PredictionHistory

class PredictionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionHistory
        fields = [
            "id", "size", "rooms", "bathrooms", "age", "location",
            "latitude", "longitude", "predicted_price", "created_at",
        ]
