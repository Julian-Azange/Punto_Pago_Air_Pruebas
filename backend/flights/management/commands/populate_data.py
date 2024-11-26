import datetime
from django.core.management.base import BaseCommand
from flights.models import Airport, Flight, Airplane, Seat


class Command(BaseCommand):
    help = "Popula la base de datos con datos iniciales de aeropuertos y vuelos"

    def handle(self, *args, **options):
        self.populate_data()

    def populate_data(self):
        # Eliminar todos los asientos antes de poblar nuevos datos
        Seat.objects.all().delete()

        # Crear aeropuertos
        airports = [
            {"code": "BOG", "name": "Bogotá"},
            {"code": "MDE", "name": "Medellín"},
            {"code": "BAQ", "name": "Barranquilla"},
            {"code": "BGA", "name": "Bucaramanga"},
            {"code": "SMR", "name": "Santa Marta"},
            {"code": "CTG", "name": "Cartagena"},
            {"code": "CLO", "name": "Cali"},
            {"code": "EOH", "name": "Enrique Olaya Herrera"},
        ]

        # Crear aeropuertos en la base de datos
        for airport_data in airports:
            Airport.objects.get_or_create(
                code=airport_data["code"], name=airport_data["name"]
            )

        # Crear aviones
        airplanes = [
            {
                "name": "Airbus A320",
                "seat_count_first_class": 12,
                "seat_count_business_class": 24,
                "seat_count_economy_class": 120,
            },
            {
                "name": "Boeing 737",
                "seat_count_first_class": 10,
                "seat_count_business_class": 20,
                "seat_count_economy_class": 100,
            },
        ]

        airplane_instances = []
        for airplane_data in airplanes:
            airplane, created = Airplane.objects.get_or_create(
                name=airplane_data["name"],
                seat_count_first_class=airplane_data["seat_count_first_class"],
                seat_count_business_class=airplane_data["seat_count_business_class"],
                seat_count_economy_class=airplane_data["seat_count_economy_class"],
            )
            airplane_instances.append(airplane)

            # Crear los asientos para cada avión
            for seat_number in range(1, airplane.seat_count_first_class + 1):
                Seat.objects.get_or_create(
                    airplane=airplane,
                    seat_number=f"F{seat_number}",
                    seat_class="first_class",
                    is_reserved=False,
                )

            for seat_number in range(1, airplane.seat_count_business_class + 1):
                Seat.objects.get_or_create(
                    airplane=airplane,
                    seat_number=f"B{seat_number}",
                    seat_class="business_class",
                    is_reserved=False,
                )

            for seat_number in range(1, airplane.seat_count_economy_class + 1):
                Seat.objects.get_or_create(
                    airplane=airplane,
                    seat_number=f"E{seat_number}",
                    seat_class="economy_class",
                    is_reserved=False,
                )

        # Crear vuelos
        flights = [
            # Vuelos directos desde Bogotá
            {
                "origin": "BOG",
                "destination": "MDE",
                "departure_time": "06:00",
                "arrival_time": "07:30",
                "days_of_week": "Monday, Wednesday, Friday",
                "airplane": airplane_instances[0],
            },
            {
                "origin": "BOG",
                "destination": "BAQ",
                "departure_time": "08:00",
                "arrival_time": "09:30",
                "days_of_week": "Tuesday, Thursday",
                "airplane": airplane_instances[1],
            },
            {
                "origin": "BOG",
                "destination": "CTG",
                "departure_time": "09:00",
                "arrival_time": "10:45",
                "days_of_week": "Monday, Saturday",
                "airplane": airplane_instances[0],
            },
            # Vuelos directos desde Medellín
            {
                "origin": "MDE",
                "destination": "SMR",
                "departure_time": "11:00",
                "arrival_time": "12:30",
                "days_of_week": "Wednesday, Friday",
                "airplane": airplane_instances[1],
            },
            {
                "origin": "MDE",
                "destination": "BGA",
                "departure_time": "13:00",
                "arrival_time": "14:15",
                "days_of_week": "Monday, Thursday",
                "airplane": airplane_instances[0],
            },
            # Vuelos directos desde Cali
            {
                "origin": "CLO",
                "destination": "CTG",
                "departure_time": "07:00",
                "arrival_time": "08:30",
                "days_of_week": "Tuesday, Thursday, Sunday",
                "airplane": airplane_instances[1],
            },
            {
                "origin": "CLO",
                "destination": "BAQ",
                "departure_time": "10:00",
                "arrival_time": "11:30",
                "days_of_week": "Wednesday, Saturday",
                "airplane": airplane_instances[0],
            },
            # Vuelos directos desde Cartagena
            {
                "origin": "CTG",
                "destination": "SMR",
                "departure_time": "15:00",
                "arrival_time": "16:00",
                "days_of_week": "Friday, Sunday",
                "airplane": airplane_instances[1],
            },
        ]

        for flight_data in flights:
            origin = Airport.objects.get(code=flight_data["origin"])
            destination = Airport.objects.get(code=flight_data["destination"])
            airplane = flight_data["airplane"]
            available_seats = (
                airplane.seat_count_first_class
                + airplane.seat_count_business_class
                + airplane.seat_count_economy_class
            )

            Flight.objects.get_or_create(
                origin=origin,
                destination=destination,
                departure_time=flight_data["departure_time"],
                arrival_time=flight_data["arrival_time"],
                days_of_week=flight_data["days_of_week"],
                airplane=airplane,
                available_seats=available_seats,
            )

        print("Datos de aeropuertos, aviones, asientos y vuelos cargados exitosamente.")
