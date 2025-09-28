from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_price, name='predict'),
    path("evaluate/", views.evaluate, name="evaluate"),
    path("history/", views.prediction_history, name="history"),
    path("clear_history/", views.clear_history, name="clear_history"),
    path("delete_history/<int:id>/", views.delete_history, name="delete_history"),
    # path("debug_cities/", views.debug_cities, name="debug_cities"),
]