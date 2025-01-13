from django.db import transaction
from ..models import Seat

def assign_seat(event):
    with transaction.atomic():
        seat = Seat.objects.select_for_update().filter(event=event, is_booked=False).first()

        if seat:
            seat.is_reserved = True
            seat.save()
            return seat
    return None