from django.db import models


class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    seat_count_first_class = models.PositiveIntegerField(default=0)
    seat_count_business_class = models.PositiveIntegerField(default=0)
    seat_count_economy_class = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Seat(models.Model):
    airplane = models.ForeignKey(
        Airplane, related_name="seats", on_delete=models.CASCADE
    )
    seat_number = models.CharField(max_length=10)
    seat_class = models.CharField(
        max_length=20,
        choices=[
            ("first_class", "Primera Clase"),
            ("business_class", "Clase Ejecutiva"),
            ("economy_class", "Clase Económica"),
        ],
    )
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"Seat {self.seat_number} ({self.seat_class}) in {self.airplane.name}"


class Flight(models.Model):
    origin = models.ForeignKey(
        Airport, related_name="departures", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Airport, related_name="arrivals", on_delete=models.CASCADE
    )
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    days_of_week = models.CharField(max_length=100)  # ej. "Monday,Wednesday,Friday"
    available_seats = models.IntegerField(default=0)
    airplane = models.ForeignKey(
        Airplane, related_name="flights", on_delete=models.CASCADE
    )  # Relación con el avión que realiza el vuelo

    def __str__(self):
        return f"Flight from {self.origin} to {self.destination}"


class Passenger(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    date_of_birth = models.DateField()
    is_infant = models.BooleanField(default=False)  # Bebé menor de 2 años

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passengers = models.ManyToManyField(Passenger)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    luggage_hand = models.BooleanField(default=False)  # Equipaje de mano (10kg)
    luggage_hold = models.BooleanField(default=False)  # Equipaje de bodega (23kg)
    extra_luggage = models.PositiveIntegerField(
        default=0
    )  # Cantidad de equipaje adicional
    meal_included = models.BooleanField(
        default=False
    )  # Si la comida está incluida (solo primera clase)
    extra_meal = models.PositiveIntegerField(
        default=0
    )  # Cantidad de comidas adicionales
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Booking for Flight {self.flight} with {len(self.passengers.all())} passengers"

    def calculate_price(self):
        base_price = 100  # Este sería el precio base del vuelo
        seat_price_multiplier = {
            "first_class": 1.0,
            "business_class": 1.05,
            "economy_class": 1.07,
        }

        # Ajuste por clase de asiento
        seat_class_multiplier = seat_price_multiplier[self.seat.seat_class]

        # Precio por cantidad de pasajeros
        passenger_count = self.passengers.count()
        price = base_price * passenger_count * seat_class_multiplier

        # Ajuste por equipaje
        if self.luggage_hold:
            price += 50  # Costo por equipaje de bodega
        if self.extra_luggage > 0:
            price += self.extra_luggage * 3 / 100  # 3% por cada equipaje adicional

        # Ajuste por comida adicional
        if self.extra_meal > 0:
            price += self.extra_meal * 1 / 100  # 1% por cada comida adicional

        # Guardar el precio total
        self.total_price = price
        self.save()


class Reservation(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passengers = models.IntegerField()
    luggage_hand = models.BooleanField(default=False)
    luggage_baggage = models.BooleanField(default=False)
    infant = models.BooleanField(default=False)
    selected_seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.flight}"
