from django.db import models
import uuid
from location_field.models.plain import PlainLocationField


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
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_free = models.BooleanField(default=False)  # Added field for free events
    city = models.CharField(max_length=255, default="")
    location = PlainLocationField(based_fields=['city'], zoom=7, default=False) # Added field for map
    number_of_tickets = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.title}"
    
    def display_price(self):
        return "Free" if self.is_free else f"${self.price}"

# Event-specific Information
class EventTicket(Ticket):
    LIVE = 'LIVE'
    ONLINE = 'ONLINE'

    EVENT_CHOICES = [
        ('LIVE','LIVE'),
        ('ONLINE','ONLINE'),
    ]

    STARTED = 'STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    NOT_STARTED = 'NOT_STARTED'

    STATUSES = (
        (NOT_STARTED, NOT_STARTED),
        (STARTED, STARTED),
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
        (CANCELLED, CANCELLED),
    )

    event_date = models.DateTimeField()
    choice = models.CharField(max_length=6, choices=EVENT_CHOICES, default=LIVE)
    has_started     = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUSES, default=NOT_STARTED)
    is_online = models.BooleanField(default=False)  # Added field for online events
    online_link = models.URLField(null=True, blank=True)  # Link for online events
    agenda = models.JSONField(default=list)  # Added field for agenda and time
    tags = models.ManyToManyField('Tag', blank=True, related_name='event_tickets')

    def __str__(self):
        return f"{self.id}"
    
    def get_status(self):
        return self.status


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
    facilities = models.JSONField(default=dict)  # Added field for facilities with descriptions

    def __str__(self):
        return f"{self.id}"

# Parking-specific Information
class ParkingTicket(Ticket):
    parking_slot = models.CharField(max_length=100)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"{self.id}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserved for {self.ticket.title}"
