from rest_framework import viewsets
from .models import Ticket, EventTicket, AccommodationTicket, ParkingTicket
from .serializers import TicketSerializer, EventTicketSerializer, AccommodationTicketSerializer, ParkingTicketSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class EventTicketViewSet(viewsets.ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = EventTicketSerializer

class AccommodationTicketViewSet(viewsets.ModelViewSet):
    queryset = AccommodationTicket.objects.all()
    serializer_class = AccommodationTicketSerializer

class ParkingTicketViewSet(viewsets.ModelViewSet):
    queryset = ParkingTicket.objects.all()
    serializer_class = ParkingTicketSerializer