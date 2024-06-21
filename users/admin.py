from django.contrib import admin

from .models import Address, Profile

# admin.site.register(PhoneNumber)
admin.site.register(Profile)
admin.site.register(Address)
