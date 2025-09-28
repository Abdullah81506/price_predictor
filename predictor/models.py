from django.db import models

# Create your models here.

class PredictionHistory(models.Model):
    size = models.IntegerField()
    rooms = models.IntegerField()
    predicted_price = models.FloatField()
    bathrooms = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)  # city name
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.size} sqft, {self.rooms} rooms in {self.location} → {self.predicted_price}k"
