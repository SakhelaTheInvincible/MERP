import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import os
from django.conf import settings


class Event(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    thumbnail = models.ImageField(upload_to='event_thumbnails/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # if no thumbnail, set the default event image
        if not self.thumbnail:
            default_thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'event_thumbnails', 'event.jpg')
            if os.path.exists(default_thumbnail_path):
                self.thumbnail = 'event_thumbnails/event.jpg'
        
        super().save(*args, **kwargs)

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError('Start date must be before end date')
        
    @property
    def duration_days(self):
        """calculate event duration"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    @property
    def is_upcoming(self):
        """check if event is upcoming"""
        return self.start_date > timezone.now()

    @property
    def can_register(self):
        """event hasn't started -> registration is possible"""
        return self.start_date > timezone.now()


class Registration(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    phone = models.CharField(max_length=20, blank=True)
    management_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['event', 'user']  # one registration per user per event
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.event.title}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def email(self):
        return self.user.email

    def can_cancel(self):
        """ check if registration can be cancelled:
        - duration must be <= 2 days
        - cancellation must be <= 2 days before event start
        """
        if self.status == 'cancelled':
            return False
            
        now = timezone.now()
        
        if self.event.duration_days > 2:
            return False
            
        days_until_event = (self.event.start_date - now).days
        if days_until_event < 2:
            return False
            
        return True

    def cancel(self):
        if not self.can_cancel():
            raise ValidationError("This registration cannot be cancelled")
        
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()

    def reactivate(self):
        """reactivate a cancelled registration"""
        if self.status != 'cancelled':
            raise ValidationError("Only cancelled registrations can be reactivated")
        
        if not self.event.can_register:
            raise ValidationError('Cannot reactivate registration for events that have already started')
        
        self.status = 'active'
        self.cancelled_at = None
        self.save()

    def clean(self):
        if self.event and not self.event.can_register:
            raise ValidationError('Cannot register for events that have already started') 