from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Ticket, EventTicket, AccommodationTicket, ParkingTicket, Reservation, Tag
from .serializers import (TicketSerializer, EventTicketSerializer, 
                          AccommodationTicketSerializer, ParkingTicketSerializer, 
                          BulkTicketSerializer, ReservationSerializer,
                          TagSerializer)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        ticket = Ticket.objects.get(pk=pk)
        user = request.user

        if Reservation.objects.filter(ticket=ticket, user=user).exists():
            return Response({"error": "You have already reserved this ticket."}, status=status.HTTP_400_BAD_REQUEST)

        reservation = Reservation.objects.create(ticket=ticket, user=user)
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        ticket = Ticket.objects.get(pk=pk)
        user = request.user

        reservation, created = Reservation.objects.get_or_create(ticket=ticket, user=user)
        reservation.is_paid = True
        reservation.save()
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)

class EventTicketViewSet(viewsets.ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = EventTicketSerializer

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'event':
            if request.data.get('is_online') and not request.data.get('online_link'):
                return Response({"error": "Online events must include an online link."}, status=status.HTTP_400_BAD_REQUEST)
            if request.data.get('agenda') and not isinstance(request.data['agenda'], list):
                return Response({"error": "Agenda must be a list of dictionaries with agenda details and times."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class AccommodationTicketViewSet(viewsets.ModelViewSet):
    queryset = AccommodationTicket.objects.all()
    serializer_class = AccommodationTicketSerializer

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'accommodation':
            if not all(k in request.data for k in ['check_in', 'check_out']):
                return Response({"error": "Accommodation must include check-in and check-out dates."}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(request.data.get('facilities', {}), dict):
                return Response({"error": "Facilities must be a dictionary with descriptions."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class ParkingTicketViewSet(viewsets.ModelViewSet):
    queryset = ParkingTicket.objects.all()
    serializer_class = ParkingTicketSerializer

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'parking':
            if not all(k in request.data for k in ['parking_slot', 'valid_from', 'valid_until']):
                return Response({"error": "Parking tickets must include parking slot, valid from, and valid until details."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class BulkTicketCreateView(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = BulkTicketSerializer(data=request.data)
        if serializer.is_valid():
            tickets = serializer.save()
            return Response({"tickets": TicketSerializer(tickets, many=True).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer