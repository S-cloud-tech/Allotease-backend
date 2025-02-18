from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Merchant

# Register your models here.
class AccountAdmin(UserAdmin):
	list_display = ('email',  'date_joined', 'last_login', 'is_admin')
	search_feilds = ('email', )
	readonly_fields = ('date_joined', 'last_login')

	filter_horizontal = ()
	list_filter = ()
	fieldsets =()
	ordering = ('email',)
	

admin.site.register(Account)
admin.site.register(Merchant)