from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Ticket),
admin.site.register(AccommodationTicket),
admin.site.register(EventTicket),
admin.site.register(ParkingTicket),
admin.site.register(Reservation),
admin.site.register(Tag),
admin.site.register(MerchantDashboard),
