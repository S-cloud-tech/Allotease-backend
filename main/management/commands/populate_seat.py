from django.core.management.base import BaseCommand
from main.models import EventTicket, Seat

class Command(BaseCommand):
    help = "Populate seats for existing event tickets"

    def handle(self, *args, **kwargs):
        tickets = EventTicket.objects.all()
        for ticket in tickets:
            existing_seats = ticket.seat
            if existing_seats == ticket.total_tickets:
                for i in range(existing_seats + 1, ticket.total_tickets + 1):
                    Seat.objects.create(ticket=ticket, seat_number=f"Seat-{i}")
                self.stdout.write(f"Seats populated for ticket: {ticket.title}")
        self.stdout.write("All tickets processed.")
