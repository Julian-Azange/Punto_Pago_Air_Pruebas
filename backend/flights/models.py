from django.db import models
from decimal import Decimal
import uuid


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

    class Meta:
        unique_together = ("airplane", "seat_number")

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
        Airplane, related_name="airplanes", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Precio en COP

    def __str__(self):
        return f"Flight from {self.origin} to {self.destination}"



class Passenger(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    date_of_birth = models.DateField()
    is_infant = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passengers = models.ManyToManyField(Passenger)
    seats = models.ManyToManyField(Seat)
    booking_date = models.DateTimeField(auto_now_add=True)
    luggage_hand = models.BooleanField(default=False)  # Equipaje de mano (10kg)
    luggage_hold = models.BooleanField(default=False)  # Equipaje de bodega (23kg)
    extra_luggage = models.PositiveIntegerField(default=0)  # Cantidad de equipaje adicional
    meal_included = models.BooleanField(default=False)  # Si la comida está incluida (solo primera clase)
    extra_meal = models.PositiveIntegerField(default=0)  # Cantidad de comidas adicionales
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def calculate_price(self): # TODO: Verificar cobro de precio
        base_price = Decimal("100.00")  # Este sería el precio base del vuelo
        seat_price_multiplier = {
            "first_class": Decimal("1.07"),
            "business_class": Decimal("1.05"),
            "economy_class": Decimal("1.00"),
        }

        # Ajuste por clase de asiento
        seat_class_multiplier = Decimal("1.00")
        for seat in self.seats.all():
            seat_class_multiplier = seat_price_multiplier.get(
                seat.seat_class, Decimal("1.0")
            )

        # Precio por cantidad de pasajeros
        passenger_count = Decimal(self.passengers.count())
        price = base_price * passenger_count * seat_class_multiplier

        # Ajuste por pasajeros menores de 2 años (gratis)
        infant_count = self.passengers.filter(is_infant=True).count()
        if infant_count > 0:
            price -= base_price * Decimal(infant_count)

        # Ajuste por equipaje
        if self.luggage_hold:
            price += Decimal("50.00")  # Costo por equipaje de bodega
        if self.extra_luggage > 0:
            price += (
                Decimal(self.extra_luggage) * Decimal("3.00") / Decimal("100.00")
            )  # 3% por cada equipaje adicional

        # Ajuste por comida adicional
        if self.extra_meal > 0:
            price += (
                Decimal(self.extra_meal) * Decimal("1.00") / Decimal("100.00")
            )  # 1% por cada comida adicional

        # Guardar el precio total
        self.total_price = price
        self.save()
        return self.total_price
    
    def __str__(self):
        return f"Booking for Flight {self.flight} with {len(self.passengers.all())} passengers"



class BookingPaymentCode(models.Model):
    payment_code = models.UUIDField(primary_key=True, default=uuid.uuid4)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __strt__(self):
        return f"Código de pago para el vuelo {self.booking.id}: {self.payment_code}"

# TODO: añadir tabla de transaccion con cod -> verificar transaccion y pago