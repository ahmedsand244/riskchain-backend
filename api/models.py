from django.db import models
from django.contrib.auth.models import User

class Shipment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('LATE', 'Late'),
        ('ON_TIME', 'On-Time')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments', null=True, blank=True)
    shipping_mode = models.CharField(max_length=50)
    order_region = models.CharField(max_length=100)
    market = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=50)
    customer_segment = models.CharField(max_length=50)
    
    scheduled_days = models.IntegerField(default=3)
    actual_duration = models.IntegerField(default=3)
    order_hour = models.IntegerField(default=10)
    order_day_of_week = models.IntegerField(default=2)
    
    predicted_risk = models.FloatField(default=0.0)
    predicted_class = models.CharField(max_length=20) # ON-TIME, LATE
    actual_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipment #{self.id} - {self.predicted_class}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message_en = models.TextField()
    message_ar = models.TextField()
    is_read = models.BooleanField(default=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username if self.user else 'System'}"

class DelayReport(models.Model):
    tracking_number = models.CharField(max_length=100)
    reporter_name = models.CharField(max_length=100, null=True, blank=True)
    reporter_email = models.EmailField(null=True, blank=True)
    message = models.TextField()
    image = models.FileField(upload_to='delay_reports/', null=True, blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.tracking_number} - {'Resolved' if self.resolved else 'Pending'}"
