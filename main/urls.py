from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, EventTicketViewSet, AccommodationTicketViewSet, ParkingTicketViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'event-tickets', EventTicketViewSet)
router.register(r'accommodation-tickets', AccommodationTicketViewSet)
router.register(r'parking-tickets', ParkingTicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]