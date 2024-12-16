from rest_framework import serializers
from .models import Ticket, EventTicket, AccommodationTicket, ParkingTicket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class EventTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTicket
        fields = '__all__'

class AccommodationTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationTicket
        fields = '__all__'

class ParkingTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingTicket
        fields = '__all__'