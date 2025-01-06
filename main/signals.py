from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EventTicket, Seat

@receiver(post_save, sender=EventTicket)
def create_seats_for_event(sender, instance, created, **kwargs):
    """
    Automatically create seats when a new EventTicket is created.
    """
    if created and instance.total_tickets > 0:
        for i in range(1, instance.total_tickets + 1):
            Seat.objects.create(ticket=instance, seat_number=f"Seat-{i}")
