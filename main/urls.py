from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (TicketViewSet, EventTicketViewSet, AccommodationTicketViewSet, 
                    ParkingTicketViewSet, BulkTicketCreateView, ReservationViewSet,
                    TagViewSet,RegisterForEventAPI, CheckInAPI)

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'event-tickets', EventTicketViewSet)
router.register(r'accommodation-tickets', AccommodationTicketViewSet)
router.register(r'parking-tickets', ParkingTicketViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterForEventAPI.as_view(), name='register'),
    path('check-in/', CheckInAPI.as_view(), name='check-in'),
    path('bulk-create-tickets/', BulkTicketCreateView.as_view({'post': 'create'})),
]
