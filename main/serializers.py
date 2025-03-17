from rest_framework import serializers
from .models import *

class TicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    is_sold_out = serializers.SerializerMethodField()
    class Meta:
        model = Ticket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()
    
    def validate(self, data):
        if data.get('location') and not data.get('city'):
            raise serializers.ValidationError("Ticket must have a location")
        return data
    
    def get_is_sold_out(self, obj):
         return obj.is_sold_out()

class TicketPurchaseSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = Ticket
        fields = ['category', 'price']

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_booked', 'row']

class EventTicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    tickets_reserved = serializers.SerializerMethodField()
    tickets_remaining = serializers.SerializerMethodField()
    seats = SeatSerializer(many=True, read_only=True)

    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = EventTicket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()
    
    def get_tickets_reserved(self, obj):
         return obj.tickets_reserved()
    
    def get_tickets_remaining(self, obj):
         return obj.tickets_remaining()
    
    def validate(self, data):
        if data.get('is_online') and not data.get('online_link'):
            raise serializers.ValidationError("Online events must have an online link.")
        if data.get('agenda') and not isinstance(data['agenda'], list):
            raise serializers.ValidationError("Agenda must be a list of dictionaries with agenda details and times.")
        return data

class AccommodationTicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    tickets_reserved = serializers.SerializerMethodField()
    tickets_remaining = serializers.SerializerMethodField()
    class Meta:
        model = AccommodationTicket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()
    
    def get_tickets_reserved(self, obj):
         return obj.tickets_reserved()
    
    def get_tickets_remaining(self, obj):
         return obj.tickets_remaining()
    
    def validate(self, data):
        if data.get('facilities') and not isinstance(data['facilities'], dict):
            raise serializers.ValidationError("Facilities must be a dictionary with descriptions.")
        return data

class ParkingTicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    tickets_reserved = serializers.SerializerMethodField()
    tickets_remaining = serializers.SerializerMethodField()
    class Meta:
        model = ParkingTicket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()
    
    def get_tickets_reserved(self, obj):
         return obj.tickets_reserved()
    
    def get_tickets_remaining(self, obj):
         return obj.tickets_remaining()

class CheckInSerialiezer(serializers.ModelSerializer):
     class Meta:
          model = CheckIn
          fields = '__all__'

class BulkTicketSerializer(serializers.Serializer):
    tickets = TicketSerializer(many=True)

    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets')
        created_tickets = []
        for ticket_data in tickets_data:
            ticket = Ticket.objects.create(**ticket_data)
            created_tickets.append(ticket)
        return created_tickets

class ReservationSerializer(serializers.Serializer):
     class Meta:
          model = Reservation
          fields = '__all__'

class SeatReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatReservation
        fields = '__all__'

class ParkingSlotReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlotReservation
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class MerchantDashboardSerializer(serializers.ModelSerializer):
     class Meta:
        model = MerchantDashboard
        fields = '__all__'

class RefundSerializer(serializers.ModelSerializer):
    ticket_code = serializers.CharField(source="ticket.ticket_code", read_only=True)
    event_name = serializers.CharField(source="ticket.event.name", read_only=True)

    class Meta:
        model = Refund
        fields = ["id", "ticket_code", "event_name", "reason", "status", "requested_at", "processed_at"]

