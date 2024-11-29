from django.db import models
from decimal import Decimal
import uuid
from nanoid import generate
from functools import partial

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
        ]
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
    price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )  # Precio en COP

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
    seat_class = models.CharField(
        max_length=20,
        choices=[
            ("first_class", "Primera Clase"),
            ("business_class", "Clase Ejecutiva"),
            ("economy_class", "Clase Económica"),
        ],
    )
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

    payment_status= models.CharField(max_length=15)
    payment_code= models.CharField(max_length=15)
    # Propiedad de código de pago, declarada así para no ser persistente puesto que es buscada.
    
    @property
    def payment_code(self):
        return BookingPaymentCode.objects.filter(booking__id=self.id).first().payment_code

    @property
    def payment_status(self):
        return BookingPaymentCode.objects.filter(booking__id=self.id).first().payment_status

    def __str__(self):
        return f"Booking for Flight {self.flight} with {len(self.passengers.all())} passengers"

    def calculate_price(self):
        base_price = self.flight.price
        seat_price_multiplier = {
            "first_class": Decimal("1.07"),
            "business_class": Decimal("1.05"),
            "economy_class": Decimal("1.00"),
        }

        # Ajuste por clase de asiento
        seat_class_multiplier = seat_price_multiplier.get(
            self.seat_class, Decimal("1.0")
        )

        total_price = Decimal("0.00")
        for passenger in self.passengers.all():
            if passenger.is_infant:
                # Precio para infante (gratis)
                continue
            else:
                # Precio para adulto o niño mayor a 2 años
                total_price += base_price * seat_class_multiplier

        # Ajuste por equipaje
        if self.luggage_hold:
            total_price += Decimal("50.00")  # Costo por equipaje de bodega
        if self.extra_luggage > 0:
            total_price += (
                Decimal(self.extra_luggage) * Decimal("3.00") / Decimal("100.00")
            )  # 3% por cada equipaje adicional

        # Ajuste por comida adicional
        if self.extra_meal > 0:
            total_price += (
                Decimal(self.extra_meal) * Decimal("1.00") / Decimal("100.00")
            )  # 1% por cada comida adicional

        # Guardar el precio total
        self.total_price = total_price
        self.save()
        return self.total_price

# TODO: Chek if relationship is Foreign key or OneToOne
class BookingPaymentCode(models.Model):
    # Enum Definition
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDIENTE'
        PAID = 'PAGADO'  
    # Attributes
    payment_code = models.UUIDField(primary_key=True, default=uuid.uuid4)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10,
                                      choices=PaymentStatus.choices,
                                      default=PaymentStatus.PENDING.value)

    def get_payment_status(self) -> PaymentStatus:
        return self.PaymentStatus(self.payment_status)


    def __str__(self):
        return f"Código de pago para el vuelo {self.booking.id}: {self.payment_code}"
    


class BookingScales(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
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
    
    @property
    def payment_code(self):
        return BookingScalePaymentCode.objects.filter(booking__id=self.id).first().payment_code

    @property
    def payment_status(self):
        return BookingScalePaymentCode.objects.filter(booking__id=self.id).first().payment_status


    def __str__(self):
        return f"Booking for Flight {self.flight} with {len(self.passengers.all())} passengers"

    def calculate_price(self):
        base_price = self.flight.price  # Precio base del vuelo
        seat_price_multiplier = {
            "first_class": Decimal("1.07"),
            "business_class": Decimal("1.05"),
            "economy_class": Decimal("1.00"),
        }

        # Ajuste por clase de asiento
        seat_class_multiplier = seat_price_multiplier.get(
            self.seat.seat_class, Decimal("1.0")
        )

        # Precio por cantidad de pasajeros
        price = base_price * seat_class_multiplier
        for passenger in self.passengers.all():
            if not passenger.is_infant:
                price += base_price * Decimal(
                    "0.10"
                )  # 10% por cada pasajero mayor de 2 años

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


class FlightSeatInstance(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return (
            f"{self.flight} - Seat {self.seat.seat} on Flight {self.date}"
        )

class BookingDetail(models.Model):
    booking = models.ForeignKey(BookingScales, on_delete=models.CASCADE)
    flightSeat = models.ForeignKey(FlightSeatInstance, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    is_stopover = models.BooleanField(default=False) 
    stopover_order = models.PositiveIntegerField(null=True, blank=True)  

    def __str__(self):
        return (
            f"{self.passenger} - Seat {self.seat.seat_number} on Flight {self.flight}"
        )


class BookingScalePaymentCode(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDIENTE'
        PAID = 'PAGADO'  
    # Attributes
    payment_code = models.CharField(primary_key=True, max_length=10)
    booking = models.ForeignKey(BookingScales, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10,
                                      choices=PaymentStatus.choices,
                                      default=PaymentStatus.PENDING.value)
    
    def save(self, *args, **kwargs):
        self.payment_code = generate(size=10)
        super(BookingScalePaymentCode, self).save(*args, **kwargs)


    def get_payment_status(self) -> PaymentStatus:
        return self.PaymentStatus(self.payment_status)


    def __str__(self):
        return f"Código de pago para el vuelo {self.booking.id}: {self.payment_code}"



# TODO: añadir tabla de transaccion con cod -> verificar transaccion y pago
