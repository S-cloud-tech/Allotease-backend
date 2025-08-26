from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'event', EventTicketViewSet)
router.register(r'accommodation', AccommodationTicketViewSet)
router.register(r'parking', ParkingTicketViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'tags', TagViewSet)
router.register(r'merchant-dashboard', MerchantDahboardViewSet)
router.register(r'check-ins', CheckInViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register-for-event/', RegisterForEventAPI.as_view(), name='register-for-event'),
    path('upload-documents/', UploadVerificationDocumentView.as_view(), name='upload-documents'),
    # path('check-in/', CheckInAPI.as_view(), name='check-in'),
    path('bulk-create-tickets/', BulkTicketCreateView.as_view({'post': 'create'})),
]
