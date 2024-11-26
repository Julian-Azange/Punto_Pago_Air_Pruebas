from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import traceback
from .models import Airport, Flight, Seat, Passenger, Booking
from .serializers import (
    FlightSerializer,
    AirportSerializer,
    BookingSerializer,
    SeatSerializer,
)
from collections import deque
import logging
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView

logger = logging.getLogger(__name__)


class AirportListView(APIView):
    def get(self, request):
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FlightSearchView(APIView):
    def get(self, request):
        origin_code = request.query_params.get("origin")
        destination_code = request.query_params.get("destination")
        date_str = request.query_params.get("date")

        if not origin_code or not destination_code or not date_str:
            return Response(
                {"error": "Origen, destino y fecha son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            day_of_week = date.strftime("%A")
        except ValueError:
            return Response(
                {"error": "Fecha en formato inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Buscar vuelos directos
        direct_flights = Flight.objects.filter(
            origin__code=origin_code,
            destination__code=destination_code,
            days_of_week__icontains=day_of_week,
        )

        direct_flight_data = []
        for flight in direct_flights:
            duration = self.calculate_duration(flight)
            hours, minutes = divmod(duration, 60)
            flight_data = FlightSerializer(flight).data
            flight_data["duration"] = f"{int(hours)} horas, {int(minutes)} minutos"
            direct_flight_data.append(flight_data)

        # Buscar rutas con escalas
        routes_with_stops = self.find_routes_with_stops(
            origin_code, destination_code, day_of_week, date
        )

        return Response(
            {
                "direct_flights": direct_flight_data,
                "routes_with_stops": routes_with_stops,
            },
            status=status.HTTP_200_OK,
        )

    def find_routes_with_stops(self, origin, destination, day_of_week, travel_date):
        routes = []
        queue = deque([(origin, [origin], 0, day_of_week, travel_date, [])])

        while queue:
            (
                current_airport,
                path,
                total_duration,
                current_day,
                current_date,
                flight_details,
            ) = queue.popleft()

            if current_airport == destination and len(path) > 2:
                hours, minutes = divmod(total_duration, 60)
                routes.append(
                    {
                        "route": path,
                        "total_duration": f"{int(hours)} horas, {int(minutes)} minutos",
                        "flights": flight_details,
                    }
                )
                continue

            connecting_flights = Flight.objects.filter(
                origin__code=current_airport, days_of_week__icontains=current_day
            )

            for flight in connecting_flights:
                if flight.destination.code not in path:
                    flight_duration = self.calculate_duration(flight)
                    departure_datetime = datetime.combine(
                        current_date, flight.departure_time
                    )
                    arrival_datetime = departure_datetime + timedelta(
                        minutes=flight_duration
                    )

                    new_duration = total_duration + flight_duration
                    new_day = current_day
                    new_date = current_date
                    if arrival_datetime.date() > departure_datetime.date():
                        new_day = self.get_next_day(current_day)
                        new_date = arrival_datetime.date()

                    new_flight_details = flight_details + [
                        {
                            "origin": flight.origin.code,
                            "destination": flight.destination.code,
                            "departure_time": departure_datetime.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "arrival_time": arrival_datetime.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    ]

                    new_path = path + [flight.destination.code]
                    queue.append(
                        (
                            flight.destination.code,
                            new_path,
                            new_duration,
                            new_day,
                            new_date,
                            new_flight_details,
                        )
                    )

        routes = sorted(routes, key=lambda x: x["total_duration"])

        return routes

    def calculate_duration(self, flight):
        fmt = "%H:%M"
        departure_time = datetime.strptime(flight.departure_time.strftime(fmt), fmt)
        arrival_time = datetime.strptime(flight.arrival_time.strftime(fmt), fmt)
        duration = (arrival_time - departure_time).total_seconds() / 60
        if duration < 0:
            duration += 24 * 60
        return duration

    def get_next_day(self, current_day):
        days_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        current_index = days_of_week.index(current_day)
        next_index = (current_index + 1) % len(days_of_week)
        return days_of_week[next_index]


class BookingView(APIView):
    def post(self, request):
        data = request.data

        try:
            flight_id = data.get("flight_id")
            passenger_info = data.get("passengers")
            seat_number = data.get("seat_number")
            luggage_hand = data.get("luggage_hand", False)
            luggage_hold = data.get("luggage_hold", False)
            extra_luggage = data.get("extra_luggage", 0)
            extra_meal = data.get("extra_meal", 0)

            if not flight_id or not passenger_info or not seat_number:
                return Response(
                    {"error": "Faltan datos requeridos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar si el vuelo existe
            flight = get_object_or_404(Flight, id=flight_id)

            # Verificar si el asiento está disponible
            try:
                seat = Seat.objects.get(
                    airplane=flight.airplane, seat_number=seat_number, is_reserved=False
                )
            except Seat.DoesNotExist:
                return Response(
                    {"error": "El asiento no está disponible."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear los pasajeros
            passengers = []
            for passenger in passenger_info:
                p = Passenger.objects.create(
                    first_name=passenger["first_name"],
                    last_name=passenger["last_name"],
                    email=passenger["email"],
                    date_of_birth=passenger["date_of_birth"],
                    is_infant=passenger.get("is_infant", False),
                )
                passengers.append(p)

            # Crear la reserva
            booking = Booking.objects.create(
                flight=flight,
                seat=seat,
                luggage_hand=luggage_hand,
                luggage_hold=luggage_hold,
                extra_luggage=extra_luggage,
                extra_meal=extra_meal,
            )
            booking.passengers.set(passengers)
            booking.calculate_price()  # Calcula el precio total y lo guarda

            # Reservar el asiento
            seat.is_reserved = True
            seat.save()

            # Serializar la respuesta
            serializer = BookingSerializer(booking)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Loguea el error detalladamente
            logger.error(f"Error al crear la reserva: {str(e)}")
            logger.error(
                traceback.format_exc()
            )  # Muestra el traceback completo para depurar
            return Response(
                {"error": "Ocurrió un error al crear la reserva."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SeatListView(APIView):
    def get(self, request, flight_id):
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return Response({"error": "Vuelo no encontrado."}, status=404)

        seats = Seat.objects.filter(airplane=flight.airplane)
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)
