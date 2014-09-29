from django.contrib import admin
from stationspinner.accounting.models import APIKey, Capsuler

class APIKeyAdmin(admin.ModelAdmin):
    readonly_fields = ('accessMask', 'type')

admin.site.register(Capsuler)
admin.site.register(APIKey, APIKeyAdmin)