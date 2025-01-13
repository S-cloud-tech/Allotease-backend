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
