from rest_framework import serializers
from .models import Ticket, EventTicket, AccommodationTicket, ParkingTicket, Reservation, Tag

class TicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    class Meta:
        model = Ticket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()

class EventTicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
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
    
    def validate(self, data):
        if data.get('is_online') and not data.get('online_link'):
            raise serializers.ValidationError("Online events must have an online link.")
        if data.get('location') and not data.get('location_address'):
             raise serializers.ValidationError("Live event must have a location")
        if data.get('agenda') and not isinstance(data['agenda'], list):
            raise serializers.ValidationError("Agenda must be a list of dictionaries with agenda details and times.")
        return data

class AccommodationTicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    class Meta:
        model = AccommodationTicket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()
    
    def validate(self, data):
        if data.get('facilities') and not isinstance(data['facilities'], dict):
            raise serializers.ValidationError("Facilities must be a dictionary with descriptions.")
        return data

class ParkingTicketSerializer(serializers.ModelSerializer):
    display_price = serializers.SerializerMethodField()
    class Meta:
        model = ParkingTicket
        fields = '__all__'

    def get_display_price(self, obj):
            return obj.display_price()

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
