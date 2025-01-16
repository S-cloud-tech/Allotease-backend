from celery import shared_task
from django.core.mail import send_mail
from .models import Ticket

@shared_task
def send_ticket_email(ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    send_mail(
        'Your Event Ticket',
        f"Hello {ticket.user.username},\n\nHere is your ticket for {ticket.event.name}. Seat: {ticket.seat.row}-{ticket.seat.seat_number}.",
        'no-reply@example.com',
        [ticket.user.email],
    )

@shared_task
def process_real_time_data(event_id, data):
    from .models import EventAnalytics
    analytics, created = EventAnalytics.objects.get_or_create(event_id=event_id)
    analytics.data.update(data)
    analytics.save()
    return f"Analytics updated for event {event_id}"
