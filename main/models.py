import os
from django.db import models
from django.utils.timezone import now
from django.conf import settings
import uuid
from location_field.models.plain import PlainLocationField
from accounts.models import Account, Merchant
from paystackapi.transaction import Transaction
from .utils.mail import send_refund_email


def receipt_upload_path(instance, filename):
    return f"receipts/{uuid.uuid4()}_{filename}"


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('event', 'Event'),
        ('accommodation', 'Accommodation'),
        ('parking', 'Parking'),
    ]

    STATUS_CHOICES = [
        ('', ''),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
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
    total_tickets = models.PositiveIntegerField(default=1)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    receipt = models.FileField(upload_to=receipt_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = self.generate_ticket_code()
        if self.status == 'paid':  # Generate QR only after payment
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    def display_price(self):
        return "Free" if self.is_free else f"${self.price}"
    
    def tickets_reserved(self):
        return Reservation.objects.filter(ticket=self).count()
    
    def tickets_remaining(self):
        return self.total_tickets - self.tickets_reserved()

    def is_sold_out(self):
        return self.tickets_remaining() <= 0
    
    def delete_old_receipt(self):
        """Delete the old receipt file if it exists"""
        if self.receipt:
            if os.path.isfile(self.receipt.path):
                os.remove(self.receipt.path)

# Seat model
class Seat(models.Model):
    # ticket = models.ForeignKey(EventTicket, on_delete=models.CASCADE, related_name="seats", null=True)
    row = models.CharField(max_length=10, null=True)
    seat_number = models.CharField(max_length=20)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Seat {self.seat_number} ({'Reserved' if self.is_booked else 'Available'})"

# Tag model
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

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
    # user = models.ForeignKey(Account, blank=False, null=True, default=None, on_delete=models.CASCADE, related_name="regular")
    # organizer = models.ForeignKey(Merchant, null=True, blank=True, default=None, on_delete=models.CASCADE, related_name="merchant")
    is_online = models.BooleanField(default=False)  # Added field for online events
    online_link = models.URLField(null=True, blank=True)  # Link for online events
    agenda = models.JSONField(default=list)  # Added field for agenda and time
    tags = models.ManyToManyField('Tag', blank=True, related_name='event_tickets')
    # seat_number = models.ManyToManyField('Seat', blank=True, related_name='event_seats')
    # seat = models.OneToOneField(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.id}"
    
    def get_status(self):
        return self.status
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new instance
        super().save(*args, **kwargs)  # Save the ticket first

        if is_new and self.total_tickets > 0:
            for i in range(1, self.total_tickets + 1):
                Seat.objects.create(ticket=self, seat_number=f"Seat-{i}")
    
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

# CheckIn
class CheckIn(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    # user = models.ForeignKey(Account, on_delete=models.CASCADE)
    check_in_time =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Check-in: {self.user.username} for {self.ticket.title}"


class Reservation(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    seat_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Reserved for {self.ticket.title}"


class SeatReservation(models.Model):
    event_ticket = models.ForeignKey(EventTicket, on_delete=models.CASCADE, related_name="reserved_seats")
    seat_number = models.CharField(max_length=10)  # Example: A1, B2
    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event_ticket', 'seat_number')  # Prevent duplicate reservations

class ParkingSlotReservation(models.Model):
    parking_ticket = models.ForeignKey(ParkingTicket, on_delete=models.CASCADE, related_name="reserved_slots")
    slot_number = models.CharField(max_length=10)  # Example: P1, P2
    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('parking_ticket', 'slot_number')  # Prevent duplicate reservations


class MerchantDashboard(models.Model):
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE)
    total_tickets = models.IntegerField(default=0)
    total_tickets_sold = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"Dashboard for {self.merchant.user.username}"

class DigitalIdentityVerification(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='digital_identity')
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verification_documents/')
    verification_date = models.DateTimeField(null=True, blank=True)

class Refund(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(
        max_length=10, choices=[("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied")], default="pending"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def approve_refund(self):
        """Mark refund as approved and process refund"""
        self.status = "approved"
        self.processed_at = now()
        self.ticket.status = "available"  # Release the ticket
        self.ticket.save()
        self.save()

    def deny_refund(self):
        """Deny the refund request"""
        self.status = "denied"
        self.processed_at = now()
        self.save()

        # Send email to user
        subject = "Refund Denied ❌"
        message = f"Hello {self.user.username}, your refund request for ticket {self.ticket.ticket_code} has been denied."
        send_refund_email(self.user.email, subject, message)

    def process_paystack_refund(self):
        """Trigger a refund request to Paystack"""
        transaction = Transaction.list(reference=self.ticket.ticket_code)
        if transaction.get("status") and transaction["data"]:
            trans_id = transaction["data"][0]["id"]
            response = Transaction.refund(trans_id, settings.PAYSTACK_SECRET_KEY)

            if response["status"]:
                self.status = "approved"
                self.processed_at = now()
                self.ticket.status = "available"  # Reset the ticket for resale
                self.ticket.save()
                self.save()
                return True
        return False

