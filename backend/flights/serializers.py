from rest_framework import serializers
from .models import Airport, Flight, Seat, Passenger, Booking, BookingScales


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
    seats = SeatSerializer(many=True)
    passengers = PassengerSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_status = serializers.ReadOnlyField()
    payment_code = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "flight",
            "passengers",
            "seats",
            "booking_date",
            "luggage_hand",
            "luggage_hold",
            "extra_luggage",
            "meal_included",
            "extra_meal",
            "total_price",
            "payment_status",
            "payment_code"
        ]



class BookingScalesCreateSerializer(serializers.ModelSerializer):
    passenger_email = serializers.EmailField(source='passenger.email', read_only=True) 

    class Meta:
        model = BookingScales
        fields = [
            'id',
            'passenger_email',
            'passenger',
            'booking_date',
            'luggage_hand',
            'luggage_hold',
            'extra_luggage',
            'meal_included',
            'extra_meal',
            'total_price',
        ]