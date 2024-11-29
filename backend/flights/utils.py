

from django.http import JsonResponse
from .models import Airplane, FlightSeatInstance, Seat


def get_available_seat(airplane_id, seat_class, departure_date, seat):

    airplane = Airplane.objects.get(id=airplane_id)
    if seat:
        occupied_seats = FlightSeatInstance.objects.filter(
            date=departure_date,
            seat__airplane=airplane,
            seat__id=seat
        )

        if occupied_seats:
            return {"error": "El asiento se encuentra ocupado"}
        else:
            return {"seat_id": seat}

    if seat_class == "first_class":
        max_seats = airplane.seat_count_first_class
    elif seat_class == "business_class":
        max_seats = airplane.seat_count_business_class
    elif seat_class == "economy_class":
        max_seats = airplane.seat_count_economy_class
    else:
        return "Invalid seat class."

    occupied_seats = FlightSeatInstance.objects.filter(
        date=departure_date,
        seat__airplane=airplane,
        seat__seat_class=seat_class
    ).values_list('seat_id', flat=True)

    # Calculate the number of available seats
    available_seats = max_seats - len(occupied_seats)

    if available_seats > 0:
        # Get the available seats that are not occupied
        available_seat = Seat.objects.filter(
            airplane=airplane,
            seat_class=seat_class
        ).exclude(
            id__in=occupied_seats  # Exclude seats that are occupied
        ).first()
        print(available_seat)

        return {"seat_id": available_seat.id}
    else:
        return {"error": "Los asientos de este vuelos estan completos"}
