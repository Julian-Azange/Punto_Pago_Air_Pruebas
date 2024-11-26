from django.urls import path
from .views import FlightSearchView, AirportListView

urlpatterns = [
    path("search/", FlightSearchView.as_view(), name="flight-search"),
    path(
        "airports/", AirportListView.as_view(), name="airport-list"
    ),  # Endpoint de aeropuertos
]
