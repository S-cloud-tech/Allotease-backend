from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .utils.mail import send_booking_email
from .models import Ticket, EventTicket, AccommodationTicket, ParkingTicket, Reservation, Tag, Seat, CheckIn
from . import serializers
from .utils.qr_code import generate_qr_code
from .utils.seat_assignment import assign_seat

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketSerializer

    permission_classes = [IsAuthenticated]

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = serializers.ReservationSerializer

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        ticket = Ticket.objects.get(pk=pk)
        user = request.user
        seat_id = request.data.get('seat_id')

        if Reservation.objects.filter(ticket=ticket, user=user).exists():
            return Response({"error": "You have already reserved this ticket."}, status=status.HTTP_400_BAD_REQUEST)
        
        if ticket.tickets_remaining() <= 0:
            return Response({"error": "No tickets remaining."}, status=status.HTTP_400_BAD_REQUEST)
        
        seat_number = request.data.get('seat_number')
        if isinstance(ticket, EventTicket) and not seat_number:
            return Response({"error": "Seat number is required for event reservations."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the seat is valid and available
        try:
            seat = Seat.objects.get(id=seat_id, ticket=ticket, is_reserved=False)
        except Seat.DoesNotExist:
            return Response({"error": "Seat is either invalid or already reserved."}, status=status.HTTP_400_BAD_REQUEST)

        # Reserve the seat
        seat.is_reserved = True
        seat.save()

        reservation = Reservation.objects.create(ticket=ticket, user=user)
        return Response(serializers.ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        ticket = Ticket.objects.get(pk=pk)
        user = request.user

        reservation, created = Reservation.objects.get_or_create(ticket=ticket, user=user)
        reservation.is_paid = True
        reservation.save()

        subject = f"Ticket Purchase Confirmation: {ticket.title}"
        html_content = render_to_string('email_templates/ticket_confirmation.html', {
            'user': user,
            'ticket': ticket,
        })
        email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        email.content_subtype = 'html'  # Use HTML content
        email.send()

        return Response(serializers.ReservationSerializer(reservation).data, status=status.HTTP_200_OK)

class EventTicketViewSet(viewsets.ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = serializers.EventTicketSerializer

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'event':
            if request.data.get('is_online') and not request.data.get('online_link'):
                return Response({"error": "Online events must include an online link."}, status=status.HTTP_400_BAD_REQUEST)
            if request.data.get('agenda') and not isinstance(request.data['agenda'], list):
                return Response({"error": "Agenda must be a list of dictionaries with agenda details and times."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    

class AccommodationTicketViewSet(viewsets.ModelViewSet):
    queryset = AccommodationTicket.objects.all()
    serializer_class = serializers.AccommodationTicketSerializer

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'accommodation':
            if not all(k in request.data for k in ['check_in', 'check_out']):
                return Response({"error": "Accommodation must include check-in and check-out dates."}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(request.data.get('facilities', {}), dict):
                return Response({"error": "Facilities must be a dictionary with descriptions."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class ParkingTicketViewSet(viewsets.ModelViewSet):
    queryset = ParkingTicket.objects.all()
    serializer_class = serializers.ParkingTicketSerializer

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'parking':
            if not all(k in request.data for k in ['parking_slot', 'valid_from', 'valid_until']):
                return Response({"error": "Parking tickets must include parking slot, valid from, and valid until details."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class RegisterForEventAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        event_id = request.data.get('event_id')

        try:
            event = EventTicket.objects.get(id=event_id)
            seat = assign_seat(event)

            if not seat:
                return Response({"error": "No available seats for this event."}, status=400)

            ticket = Ticket.objects.create(user=user, event=event, seat=seat)
            qr_data = f"Ticket ID: {ticket.id}, Event: {event.name}, Seat: {seat.row}-{seat.seat_number}"
            ticket.qr_code.save(f"ticket_{ticket.id}.png", generate_qr_code(qr_data))

            serializer = serializers.TicketSerializer(ticket)
            return Response(serializer.data)

        except EventTicket.DoesNotExist:
            return Response({"error": "Event not found."}, status=404)

class CheckInAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket_id = request.data.get('ticket_id')

        try:
            ticket = Ticket.objects.get(id=ticket_id)
            CheckIn.objects.create(ticket=ticket)
            return Response({"message": "Check-in successful."})
        except Ticket.DoesNotExist:
            return Response({"error": "Invalid ticket."}, status=404)

class BulkTicketCreateView(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = serializers.BulkTicketSerializer(data=request.data)
        if serializer.is_valid():
            tickets = serializer.save()
            return Response({"tickets": serializers.TicketSerializer(tickets, many=True).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer