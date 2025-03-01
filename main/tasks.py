from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from .models import Ticket

@shared_task
def send_ticket_email(ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    send_mail(
        'Your Event Ticket',
        f"Hello {ticket.user.username},\n\nHere is your ticket for {ticket.event.name}. Seat: {ticket.seat.row}-{ticket.seat.seat_number}.",
        'allotease2@gmail.com',
        [ticket.user.email],
    )

@shared_task
def process_real_time_data(event_id, data):
    from .models import EventAnalytics
    analytics, created = EventAnalytics.objects.get_or_create(event_id=event_id)
    analytics.data.update(data)
    analytics.save()
    return f"Analytics updated for event {event_id}"

@shared_task
def delete_old_receipts():
    threshold = now() - timedelta(days=30)  # Delete receipts older than 30 days
    old_orders = Ticket.objects.filter(receipt__isnull=False, created_at__lt=threshold)
    
    for order in old_orders:
        order.delete_old_receipt()  # Remove file
        order.receipt = None  # Clear field
        order.save()
