from django.contrib import admin
from .models import Airport, BookingDetail, BookingScales, Flight, Passenger, Seat, Airplane, BookingPaymentCode


# Register your models here.
admin.site.register(Airport)
admin.site.register(BookingDetail)
admin.site.register(BookingScales)
admin.site.register(Flight)
admin.site.register(Passenger)
admin.site.register(Seat)
admin.site.register(Airplane)
admin.site.register(BookingPaymentCode)