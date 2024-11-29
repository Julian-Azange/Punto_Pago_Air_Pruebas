from decimal import Decimal
from .utils import get_available_seat
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import traceback
from .email_helper import EmailHelper
from django.db.models import Prefetch
from django.db.models import Count

from .models import Airplane, Airport, BookingDetail, BookingScales, Flight, FlightSeatInstance, Seat, Passenger, Booking, BookingPaymentCode
from .serializers import (
    FlightSerializer,
    AirportSerializer,
    BookingSerializer,
    SeatSerializer,
)
from math import fsum
from collections import deque
import logging
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from .serializers import BookingScalesCreateSerializer
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

        if not origin_code or not destination_code:
            return Response(
                {"error": "Origen y destino son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not date_str:
            return Response(
                {"error": "Fecha es requerida."}, status=status.HTTP_400_BAD_REQUEST
            )

        day_of_week = self.format_date(date_str)

        # Buscar vuelos directos
        direct_flights = Flight.objects.filter(
            origin__code=origin_code,
            destination__code=destination_code,
            days_of_week__icontains=day_of_week,
        )

        direct_flight_data = self.append_direct_flight_data(direct_flights, date_str)

        # Buscar rutas con escalas
        routes_with_stops = self.find_routes_with_stops(
            origin_code, destination_code, day_of_week, date_str
        )

        return Response(
            direct_flight_data + routes_with_stops, status=status.HTTP_200_OK
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
                precio_total = fsum(flight["price"] for flight in flight_details)
                routes.append(
                    {
                        "id": flight_details[0].get("id"),
                        "origin": {
                            "code": flight_details[0]["origin"],
                            "name": Airport.objects.get(
                                code=flight_details[0]["origin"]
                            ).name,
                        },
                        "destination": {
                            "code": flight_details[-1]["destination"],
                            "name": Airport.objects.get(
                                code=flight_details[-1]["destination"]
                            ).name,
                        },
                        "fecha_inicio": flight_details[0]["departure_time"],
                        "fecha_final": flight_details[-1]["arrival_time"],
                        "duracion": f"{int(hours)} horas, {int(minutes)} minutos",
                    
                        "precio": float(precio_total),
                        "vuelos": flight_details,
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
                        datetime.strptime(current_date, "%Y-%m-%d"),
                        flight.departure_time,
                    )
                    arrival_datetime = departure_datetime + timedelta(
                        minutes=flight_duration
                    )

                    new_duration = total_duration + flight_duration
                    new_day = current_day
                    new_date = current_date
                    if arrival_datetime.date() > departure_datetime.date():
                        new_day = self.get_next_day(current_day)
                        new_date = arrival_datetime.date().strftime("%Y-%m-%d")

                    new_flight_details = flight_details + [
                        {
                            "id": flight.id,
                            "origin": flight.origin.code,
                            "destination": flight.destination.code,
                            "departure_time": departure_datetime.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "arrival_time": arrival_datetime.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "price": float(flight.price),
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

        return routes

    def format_date(self, date_str: str) -> str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.strftime("%A")
        except ValueError:
            return Response(
                {"error": "Fecha en formato inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def calculate_duration(self, flight):
        fmt = "%H:%M"
        departure_time = datetime.strptime(flight.departure_time.strftime(fmt), fmt)
        arrival_time = datetime.strptime(flight.arrival_time.strftime(fmt), fmt)
        duration = (arrival_time - departure_time).total_seconds() / 60
        if duration < 0:
            duration += 24 * 60
        return duration

    def append_direct_flight_data(self, direct_flights, date_str):
        direct_flight_data = []
        for flight in direct_flights:
            duration = self.calculate_duration(flight)
            hours, minutes = divmod(duration, 60)
            flight_data = FlightSerializer(flight).data
            flight_data.update(
                {
                    "fecha_inicio": f"{date_str} {flight.departure_time}",
                    "fecha_final": f"{date_str} {flight.arrival_time}",
                    "duracion": f"{int(hours)} horas, {int(minutes)} minutos",
                    "precio": float(flight.price),
                    "vuelos": [
                        {
                            "id": flight.id,
                            "origin": flight.origin.code,
                            "destination": flight.destination.code,
                            "departure_time": f"{date_str} {flight.departure_time}",
                            "arrival_time": f"{date_str} {flight.arrival_time}",
                            "price": float(flight.price),
                        }
                    ],
                }
            )
            direct_flight_data.append(flight_data)
        return direct_flight_data


class BookingView(APIView):
    def post(self, request):
        data = request.data

        try:
            flight_id = data.get("flight_id")
            passenger_info = data.get("passengers")
            luggage_hand = data.get("luggage_hand", False)
            luggage_hold = data.get("luggage_hold", False)
            extra_luggage = data.get("extra_luggage", 0)
            extra_meal = data.get("extra_meal", 0)

            if not flight_id or not passenger_info:
                return Response(
                    {
                        "error": "Faltan el id del vuelo o información del/los pasajeros."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar si el vuelo existe
            flight = get_object_or_404(Flight, id=flight_id)

            # Verificar la disponibilidad de asientos
            required_seats = len(passenger_info)
            available_seats = Seat.objects.filter(
                airplane=flight.airplane, is_reserved=False
            )[:required_seats]

            if len(available_seats) < required_seats:
                return Response(
                    {"error": "No hay suficientes asientos disponibles."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear los pasajeros
            passengers = self.save_passengers_list(passenger_info)

            # Crear la reserva
            booking = Booking.objects.create(
                flight=flight,
                luggage_hand=luggage_hand,
                luggage_hold=luggage_hold,
                extra_luggage=extra_luggage,
                extra_meal=extra_meal,
            )

            booking.passengers.set(passengers)
            booking.seats.set(available_seats)

            # Marcar los asientos como reservados
            for seat in available_seats:
                seat.is_reserved = True
                seat.save()

            # Calcular el precio total
            booking.total_price = booking.calculate_price()
            booking.save()

            bookingPayment = BookingPaymentCode.objects.create(
                booking=booking
            )

            # Enviar correo con el código de pago 

            #self.send_email_payment_code(str(bookingPayment.payment_code))

            # Serializar la respuesta
            serializer = BookingSerializer(booking)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Flight.DoesNotExist:
            return Response(
                {"error": "Vuelo no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error al crear la reserva: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"error": f"Ocurrió un error al crear la reserva: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

    def send_email_payment_code(self, payment_code):
        if not payment_code:
            return Response({"error":"Un error inesperado ocurrió, lo sentimos."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            EmailHelper.send_payment_email(payment_code)


    def save_passengers_list(self, passenger_info):
        passengers = [
            Passenger.objects.create(
                first_name=passenger["first_name"],
                last_name=passenger["last_name"],
                email=passenger["email"],
                date_of_birth=passenger["date_of_birth"],
                is_infant=passenger.get("is_infant", False),
            )
            for passenger in passenger_info
        ]
        return passengers



class BookingDetailView(RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get(self, request, pk):
        email = request.GET.get("email")

        if not email:
            return Response(
                {"error": "El Correo es requerido para consultar una reserva."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking = Booking.objects.filter(id=pk, passengers__email=email)
        if not booking:
            return Response(
                {"error": "El vuelo no fue encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BookingSerializer(booking, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self):
        try:
            return super().get_object()
        except Booking.DoesNotExist:
            raise NotFound(
                detail="La reserva solicitada no existe o ha sido eliminada."
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


class BookingPaymentDetailView(APIView):

    def get(self, request, booking_id) -> Response:
        email = request.GET.get("email")

        if not email:
            return Response({"error":"Email es requerido para consultar código de pago de una reserva."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        booking = Booking.objects.filter(id=booking_id).prefetch_related(
            Prefetch('passengers', queryset=Passenger.objects.filter(email=email))#  passengers__email=email
        )
 
        if not booking:
            return Response(
                {"error": "Reservación con id y/o email dado no existe"},
                status=status.HTTP_400_BAD_REQUEST)
        # TODO: check if its "first()" according to relationship
        bookingPaymentCode = BookingPaymentCode.objects.filter(
            booking_id=booking_id
        ).first()

        return Response({"code": {bookingPaymentCode.payment_code}}, 
                        status=status.HTTP_200_OK)

class BookingPaymentPayView(APIView):
    # Verifica que un coódigo de pago sea el correcto, simulando un pago real -> planteado para implementar con api de algun email y verificar con base de datos.
    # TODO: añadir arg datos de pago,
    def get(self, request, booking_id) -> Response:

        payment_code = request.GET.get("code")

        if not payment_code:
            return Response(
                {"error": "El código de pago es requerido para pagar la reserva."},
                status=status.HTTP_400_BAD_REQUEST)
        
        email = request.GET.get("email")

        if not email:
            return Response({"error":"Email es requerido para pagar la reserva."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        booking = Booking.objects.filter(id=booking_id).prefetch_related(
            Prefetch('passengers', queryset=Passenger.objects.filter(email=email))
        )
        
        if not booking:
            return Response({"error": "Reservación con id y/o email dado no existe"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Checks if a payment code corresponds to a booking by its id and by the passenger email associated to that booking
        booking_payment_code = BookingPaymentCode.objects.filter(payment_code=payment_code).prefetch_related(
                                    Prefetch('booking', queryset = Booking.objects.filter(id=booking_id).prefetch_related
                                                (Prefetch('passengers',queryset=Passenger.objects.filter(email=email)))
                                            )
                                    )
        
        if not booking_payment_code:
            return Response({"error":"El código de pago y/o email del pasajero no corresponde a la reseva dada."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Updates the status of the bokking to 'pagado'
        BookingPaymentCode.objects.filter(booking__id=booking_id, booking__passengers__email=email).update(
                payment_status = BookingPaymentCode.PaymentStatus.PAID.value
            )
        
        return Response(
                {"success": "Vuelo pagado correctamente."}, 
                status=status.HTTP_200_OK)
        
        

class BookingScalesView(APIView):
    def post(self, request):
        data = request.data

        try:
            
            passenger_info = data.get("passengers")
        
            luggage_hand = data.get("luggage_hand", False)
            luggage_hold = data.get("luggage_hold", False)
            extra_luggage = data.get("extra_luggage", 0)
            extra_meal = data.get("extra_meal", 0)
            departure_date = data.get("departure_date")



            if not passenger_info or not departure_date:
                return Response(
                    {"error": "Faltan datos requeridos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            list_seat_flights = [d["flight_ids"] for d in passenger_info]
            
            #Validar, que tengan las mismas cantidad de asientos  y vuelos, que existan asientos disponibles, si no trae asientos asignarle automaticamente
            #Fala la funcion, datos entrada list_seat_flights =  [{'1': 'E1', '2': 'E2'}, {'154': 'E1', '254': 'E2'}]
            #{'id del Vuelo': 'Asiento seleecionado', '2': 'E2'}

            
            # print(list_seat_flights)

            # return Response({"ok":"hola"}, status=status.HTTP_201_CREATED)

            # Validar que la cantidad de vuelos y asientos proporcionados coincidan
 
            total_price = Decimal(
                "0.00"
            )  # Inicializar el precio total para toda la reserva


            # Reservar cada vuelo de la ruta
            # Crear la reserva para el vuelo actual
            
            booking_passenger = passenger_info[0]
            newpassengerBooking = Passenger.objects.create(
                    first_name=booking_passenger["first_name"],
                    last_name=booking_passenger["last_name"],
                    email=booking_passenger["email"],
                    date_of_birth=booking_passenger["date_of_birth"],
                    is_infant=False,
                )

            newBooking = BookingScales.objects.create(
                passenger =newpassengerBooking,
                luggage_hand=luggage_hand,
                luggage_hold=luggage_hold,
                extra_luggage=extra_luggage,
                extra_meal=extra_meal,
            )
            


            # Crear los pasajeros (esto es común para todos los vuelos de la ruta)
            for passenger in passenger_info:

                #Crear pasajero - Valdiar si ya existe ese pasajero con el email
                p = Passenger.objects.create(
                    first_name=passenger["first_name"],
                    last_name=passenger["last_name"],
                    email=passenger["email"],
                    date_of_birth=passenger["date_of_birth"],
                    is_infant=passenger.get("is_infant", False),
                )


                # for flight, seat in passenger.get("flight_ids").items():
                for index, (flight, seat) in enumerate(passenger.get("flight_ids").items(), start=0):

                    flight_instance = Flight.objects.get(id=int(flight))
                    seat_class = passenger.get("seat_class")
                    
                    resp_seat = get_available_seat(flight_instance, seat_class, departure_date, seat)
                    print(resp_seat)
                    if "error" in resp_seat:
                        return Response({"error": resp_seat["error"]}, status=status.HTTP_404_NOT_FOUND)
                    
                    seat_class = resp_seat.get("seat_id")


                    seat_instance = Seat.objects.get(id=int(seat_class))     

                    #Validar si los asientos estan disponibles, esto es en newFlightSeat, con la fecha y vuelo y asiento
                    # o si no crear

                    newFlightSeat = FlightSeatInstance.objects.create(
                        seat=seat_instance,
                        flight=flight_instance,
                        date=departure_date
                    )

                    is_stopover = False

                    if len(passenger.get("flight_ids").keys())>1 and index > 0:
                        is_stopover = True
                        stopover_order = index

                    newBookingDetail = BookingDetail.objects.create(
                        booking = newBooking,
                        flightSeat = newFlightSeat,
                        passenger =p,
                        is_stopover = is_stopover,
                        stopover_order = index
                    )

            
            serializer = BookingScalesCreateSerializer(newBooking)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Flight.DoesNotExist:
            return Response(
                {"error": "Vuelo no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error al crear la reserva: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"error": f"Ocurrió un error al crear la reserva: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SeatAvailabilityView(APIView):
    def get(self, request, flight_id, date):
        # Obtiene la aeronave
        try:
            flight = Flight.objects.get(id=flight_id)
            airplane = flight.airplane
        except Flight.DoesNotExist:
            raise NotFound("Airplane not found")

        # Cuenta de asientos disponibles por clase
        seat_counts = {
            "first_class_available": airplane.seat_count_first_class,
            "business_class_available": airplane.seat_count_business_class,
            "economy_class_available": airplane.seat_count_economy_class,
        }

        # Obtiene los asientos ya reservados para el avión y la fecha
        reserved_seats = (
            FlightSeatInstance.objects.filter(
                seat__airplane=airplane,
                date=date,
            )
            .values("seat__seat_class")
            .annotate(count=Count("seat"))
        )


        # Resta los asientos reservados por clase
        for seat in reserved_seats:
            print("seat")
            print(seat)
            seat_class = seat["seat__seat_class"]
            reserved_count = seat["count"]
            if seat_class == "first_class":
                seat_counts["first_class_available"] -= reserved_count
            elif seat_class == "business_class":
                seat_counts["business_class_available"] -= reserved_count
            elif seat_class == "economy_class":
                seat_counts["economy_class_available"] -= reserved_count

        # Evita valores negativos
        seat_counts = {k: { "cant_seat" : max(0, v)} for k, v in seat_counts.items()}
        
        seat_counts["first_class_available"]["percentage"] = 1.5
        seat_counts["business_class_available"]["percentage"] = 1.2
        seat_counts["economy_class_available"]["percentage"] = 1

        return Response(seat_counts)