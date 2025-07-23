from django.contrib import admin
from django.shortcuts import redirect
from .models import Event, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'duration_days', 'is_upcoming']
    list_filter = ['start_date', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'duration_days', 'is_upcoming', 'can_register']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'thumbnail')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Read-only Information', {
            'fields': ('duration_days', 'is_upcoming', 'can_register', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def add_view(self, request, form_url='', extra_context=None):
        """Redirect to custom event creation page instead of admin form"""
        return redirect('/create/')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'event', 'status', 'created_at', 'can_cancel']
    list_filter = ['status', 'event', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'event__title']
    readonly_fields = ['management_code', 'created_at', 'updated_at', 'cancelled_at', 'can_cancel']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone')
        }),
        ('Event', {
            'fields': ('event',)
        }),
        ('Registration Details', {
            'fields': ('status', 'management_code', 'can_cancel')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(['event', 'user'])
        return readonly 