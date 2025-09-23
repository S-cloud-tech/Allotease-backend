from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Count, Sum
from .utils.mail import send_booking_email, generate_shareable_links
from .models import *
from . import serializers
from .utils.qr_code import generate_qr_code, save_receipt
from .utils.seat_assignment import assign_seat
from .utils.verification import verify_document_with_third_party
import json



def confirm_order(request, tickect_id):
    order = get_object_or_404(Ticket, id=tickect_id, user=request.user)
    save_receipt(order)  # Generate and save the receipt
    return FileResponse(order.receipt.open(), content_type='application/pdf')


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketSerializer

    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='purchase')
    def purchase_ticket(self, request):
        """
        API endpoint to purchase a ticket.
        Usage: POST /main/tickets/purchase/
        """
        serializer = serializers.TicketPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save(user=request.user, status='')
            return Response({
                'message': 'Ticket created. Proceed to payment.',
                'ticket_id': ticket.id,
                'amount': ticket.price
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='confirm-payment')
    def confirm_payment(self, request, pk=None):
        """
        API endpoint to confirm payment and generate a QR code.
        Usage: POST /main/tickets/{ticket_id}/confirm-payment/
        """
        ticket = get_object_or_404(Ticket, pk=pk, user=request.user, status='pending')
        ticket.status = 'paid'
        ticket.save()
        self.send_qr_code_email(ticket)
        return Response({'message': 'Payment confirmed. QR code sent to email.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def check_sold_out(self, request, pk=None):
        """
        API endpoint to check if ticket is sold out.
        Usage: POST /main/tickets/{ticket_id}/check-sold-out/
        """
        ticket = self.get_object()
        return Response({"is_sold_out": ticket.is_sold_out()})
    
    @action(detail=True, methods=['get'])
    def share(self, request, pk=None):
        ticket = self.get_object()
        shareable_link = generate_shareable_links(ticket)
        return Response({"shareable_link": shareable_link})

    @action(detail=True, methods=['get'], url_path='validate')
    def validate(self, request, pk=None):
        """
        API endpoint to validate ticket.
        Usage: POST /main/tickets/{ticket_id}/validate/
        """
        ticket = get_object_or_404(Ticket, id=pk)
        serializer = self.get_serializer(ticket)
        return Response({'message': 'Ticket is valid', 'ticket': serializer.data})

    def send_qr_code_email(self, ticket):
        """Send an email with the ticket QR code attached."""
        subject = f"Your Ticket for {ticket.event_name}"
        message = f"Hello,\n\nYour ticket has been generated successfully. Please find your QR code attached.\n\nTicket Code: {ticket.ticket_code}\n\nThank you for your purchase!"
        recipient_email = ticket.user.email
        
        if ticket.qr_code:
            email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            qr_code_path = ticket.qr_code.path

            # Attach the QR code
            if os.path.exists(qr_code_path):
                email.attach_file(qr_code_path)

            email.send()

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = serializers.ReservationSerializer

    @action(detail=True, methods=['post'])
    def reserve_seat(self, request, pk=None):
        """Reserve a seat for an event ticket."""
        event_ticket = EventTicket.objects.get(pk=pk)
        seat_number = request.data.get('seat_number')
        user = request.user

        if SeatReservation.objects.filter(event_ticket=event_ticket, seat_number=seat_number).exists():
            return Response({"error": "Seat already reserved."}, status=status.HTTP_400_BAD_REQUEST)

        seat_reservation = SeatReservation.objects.create(event_ticket=event_ticket, seat_number=seat_number, user=user)
        return Response(serializers.SeatReservationSerializer(seat_reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reserve_parking_slot(self, request, pk=None):
        """Reserve a parking slot."""
        parking_ticket = ParkingTicket.objects.get(pk=pk)
        slot_number = request.data.get('slot_number')
        user = request.user

        if ParkingSlotReservation.objects.filter(parking_ticket=parking_ticket, slot_number=slot_number).exists():
            return Response({"error": "Parking slot already reserved."}, status=status.HTTP_400_BAD_REQUEST)

        slot_reservation = ParkingSlotReservation.objects.create(parking_ticket=parking_ticket, slot_number=slot_number, user=user)
        return Response(serializers.ParkingSlotReservationSerializer(slot_reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """Complete a ticket purchase and send an email confirmation."""
        reservation = self.get_object()
        reservation.is_paid = True
        reservation.save()

        # Send email confirmation
        send_mail(
            "Ticket Purchase Confirmation",
            f"Dear {reservation.user.username}, your ticket for {reservation.ticket.title} has been successfully purchased!",
            settings.DEFAULT_FROM_EMAIL,
            [reservation.user.email],
            fail_silently=False,
        )

        return Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)

class EventTicketViewSet(viewsets.ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = serializers.EventTicketSerializer

    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'event':
            if request.data.get('is_online') and not request.data.get('online_link'):
                return Response({"error": "Online events must include an online link."}, status=status.HTTP_400_BAD_REQUEST)
            if request.data.get('agenda') and not isinstance(request.data['agenda'], list):
                return Response({"error": "Agenda must be a list of dictionaries with agenda details and times."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    

    @action(detail=False, methods=['get'], url_path="analytics")
    def event_analytics(self, request):
        """
        API endpoint to generate analytics report.
        Usage: POST /main/events/analytics/
        """
        events = EventTicket.objects.annotate(
            total_tickets_sold=Count('ticket', filter=models.Q(ticket__status='paid')),
            total_revenue=Sum('ticket__price', filter=models.Q(ticket__status='paid'))
        ).values('name', 'date', 'total_tickets_sold', 'total_revenue')

        return Response({"events": list(events)}, status=200)
    
class AccommodationTicketViewSet(viewsets.ModelViewSet):
    queryset = AccommodationTicket.objects.all()
    serializer_class = serializers.AccommodationTicketSerializer

    permission_classes = [AllowAny]

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

    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if request.data.get('category') == 'parking':
            if not all(k in request.data for k in ['parking_slot', 'valid_from', 'valid_until']):
                return Response({"error": "Parking tickets must include parking slot, valid from, and valid until details."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class RegisterForEventAPI(APIView):
    permission_classes = [AllowAny]

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
            ticket.qr_code.save(f"ticket_{ticket.id}.png", generate_qr_code(qr_data)) # Generation of QR code that stores data of the event registered for

            serializer = serializers.TicketSerializer(ticket)
            return Response(serializer.data)

        except EventTicket.DoesNotExist:
            return Response({"error": "Event not found."}, status=404)

class CheckInViewSet(viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = serializers.CheckInSerialiezer

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        ticket = Ticket.objects.get(pk=pk)
        user = request.user

        if CheckIn.objects.filter(ticket=ticket, user=user).exists():
            return Response({"error": "User has already checked in."}, status=status.HTTP_400_BAD_REQUEST)
        
        check_in = CheckIn.objects.create(ticket=ticket, user=user)
        return Response(serializers.CheckInSerialiezer(check_in).data, status=status.HTTP_201_CREATED)

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

class MerchantDahboardViewSet(viewsets.ModelViewSet):
    queryset = MerchantDashboard.objects.all()
    serializer_class = serializers.MerchantDashboardSerializer

    def retrieve(self, request, pk=None):
        dashboard, _ = MerchantDashboard.objects.get_or_create(merchant_id=pk)
        serializer = serializers.MerchantDashboardSerializer(dashboard)
        return Response(serializer.data)

class UploadVerificationDocumentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user
        file = request.FILES.get("document")

        if not file:
            raise ValidationError("Verification document is required.")

        digital_identity, created = DigitalIdentityVerification.objects.get_or_create(user=user)
        digital_identity.verification_document = file
        digital_identity.save()

        # Simulate verification with a third-party service
        document_path = digital_identity.verification_document.path
        is_verified = verify_document_with_third_party(document_path)

        if is_verified:
            digital_identity.is_verified = True
            digital_identity.verification_date = now()
            digital_identity.save()
            return Response({"detail": "Document verification successful."})

        return Response({"detail": "Document verification failed."}, status=400)




