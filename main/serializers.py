from rest_framework import serializers
from .models import Ticket, EventTicket, AccommodationTicket, ParkingTicket, Reservation, Tag, Seat

class TicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    class Meta:
        model = Ticket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()
    
    def validate(self, data):
        if data.get('location') and not data.get('city'):
            raise serializers.ValidationError("Ticket must have a location")
        return data

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_booked']

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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

