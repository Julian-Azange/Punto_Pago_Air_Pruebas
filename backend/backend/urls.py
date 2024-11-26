"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from flights import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/airports/", views.AirportListView.as_view(), name="airport-list"),
    path("api/flights/search/", views.FlightSearchView.as_view(), name="flight-search"),
    path("api/bookings/", views.BookingView.as_view(), name="booking"),
    path(
        "api/flights/<int:flight_id>/seats/",
        views.SeatListView.as_view(),
        name="seat-list",
    ),
    path(
        "api/bookings/<int:pk>/",
        views.BookingDetailView.as_view(),
        name="booking-detail",
    )

]
# path("api/reservation/<int:reservation:id>/payment-code", views.ReservationPaymentDetailView.as_view(), name="reservation")