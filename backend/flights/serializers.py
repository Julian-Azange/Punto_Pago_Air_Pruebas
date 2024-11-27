from rest_framework import serializers
from .models import Airport, Flight, Seat, Passenger, Booking


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["code", "name"]


class FlightSerializer(serializers.ModelSerializer):
    origin = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Flight
        fields = [
            "id",
            "origin",
            "destination",
            "departure_time",
            "arrival_time",
            "days_of_week",
        ]


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "airplane", "seat_number", "seat_class", "is_reserved"]


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ["first_name", "last_name", "email", "date_of_birth", "is_infant"]


class BookingSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    seat = SeatSerializer()
    passengers = PassengerSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Booking
        fields = [
            "id",
            "flight",
            "seat",
            "passengers",
            "luggage_hand",
            "luggage_hold",
            "extra_luggage",
            "extra_meal",
            "total_price",
            "booking_date",
        ]
