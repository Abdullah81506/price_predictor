from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.predict_price, name='predict'),
    path("evaluate/", views.evaluate, name="evaluate"),
    path("history/", views.prediction_history, name="history"),
    path("clear_history/", views.clear_history, name="clear_history"),
    path("delete_history/<int:id>/", views.delete_history, name="delete_history"),

    # API endpoints
    path("api/predict/", api_views.predict_price_api, name="api_predict"),
    path("api/history/", api_views.prediction_history_api, name="api_history"),
]