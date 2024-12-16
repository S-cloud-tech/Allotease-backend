from django.db import models
import uuid


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('event', 'Event'),
        ('accommodation', 'Accommodation'),
        ('parking', 'Parking'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.title}"

# Event-specific Information
class EventTicket(Ticket):
    event_date = models.DateTimeField()


# Accommodation-specific Information
class AccommodationTicket(Ticket):
    ACCOMMODATION_CHOICES = [
        ('hotel & lodging', 'Hotel & lodging'),
        ('apartments', 'Apartments'),
        ('school lodges', 'School lodges'),
    ]
    choice = models.CharField(max_length=255, choices=ACCOMMODATION_CHOICES, default="apartments")
    check_in = models.DateField()
    check_out = models.DateField()

# Parking-specific Information
class ParkingTicket(Ticket):
    parking_slot = models.CharField(max_length=100)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()


