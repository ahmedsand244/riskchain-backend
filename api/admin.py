from django.contrib import admin
from .models import Shipment, Notification, DelayReport

admin.site.register(Shipment)
admin.site.register(Notification)
admin.site.register(DelayReport)
