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
        "api/bookings/<int:pk>",
        views.BookingDetailView.as_view(),
        name="booking-detail",
    ),
    path(
        "api/bookings/payments/<int:booking_id>",
        views.BookingPaymentDetailView.as_view(),
        name="booking-payment-detail",
    ),
    path(
        "api/bookings/payments/<int:booking_id>/pay",
        views.BookingPaymentPayView.as_view(),
        name="booking-payment-pay",
    ),
    
    path("api/bookings_scales/", views.BookingScalesView.as_view(), name="booking_scales"),
    path("api/bookings-scales/<int:booking_id>/", views.BookingScalesViewDetails.as_view(), name="booking_scales_details"),
    path('api/flight/<int:flight_id>/availability/<str:date>/', views.SeatAvailabilityView.as_view(), name='seat-availability'),
    path("api/bookings-scales/payments/<int:booking_id>",views.BookingScalePaymentDetailView.as_view(), name="booking-scales-payment-detail"),
    path("api/bookings-scales/payments/pay/<int:booking_id>",views.BookingScalePaymentView.as_view(), name="booking-scales-payment")
]