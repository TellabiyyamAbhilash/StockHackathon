from django.contrib import admin
from .models import User,user_otps,stocks

# Define the admin class for the User model
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'fullname', 'lastname', 'available_margin', 'used_margin', 'available_cash')
    search_fields = ('email', 'fullname', 'lastname')
    list_filter = ('is_active', 'is_staff')

# Register the User model with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(user_otps)
admin.site.register(stocks)

