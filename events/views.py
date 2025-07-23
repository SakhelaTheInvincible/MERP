from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden
from .models import Event, Registration
from .serializers import (
    EventSerializer, EventCreateSerializer, RegistrationCreateSerializer,
    RegistrationSerializer, RegistrationManagementSerializer
)

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class EventViewSet(viewsets.ViewSet):
    """EventViewSet handles all event-related operations"""
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'create_ui']: # only admin can create events
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def list(self, request):
        """list all events"""
        queryset = Event.objects.all().order_by('start_date')
        serializer = EventSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """list all upcoming events (end date is in the future)"""
        queryset = Event.objects.filter(end_date__gt=timezone.now()).order_by('start_date')
        serializer = EventSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """list all past events"""
        queryset = Event.objects.filter(end_date__lte=timezone.now()).order_by('-end_date')
        serializer = EventSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """get specific event"""
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """create a new event - admin only"""
        serializer = EventCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        response_serializer = EventSerializer(event, context={'request': request})
        return Response(
            {
                'message': 'Event created successfully!',
                'event': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], url_path='ui/list')
    def list_ui(self, request):
        """web UI for listing events"""
        return render(request, 'events/events_list.html')

    @action(detail=True, methods=['get'], url_path='ui/detail')
    def detail_ui(self, request, pk=None):
        """web UI for event details"""
        event = get_object_or_404(Event, id=pk)
        return render(request, 'events/event_detail.html', {'event': event})

    @method_decorator(login_required)
    @action(detail=False, methods=['get'], url_path='ui/create')
    def create_ui(self, request):
        """web UI for creating events"""
        if not request.user.is_staff:
            return HttpResponseForbidden("Only admin users can create events.")
        return render(request, 'events/event_create.html')


class RegistrationViewSet(viewsets.ViewSet):
    """RegistrationViewSet handles all registration-related operations"""
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """new registration for an event"""
        serializer = RegistrationCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()

        # send management code via email
        email_sent = False
        try:
            send_mail(
                subject=f'Magic Events - Registration Confirmation for {registration.event.title}',
                message=f'Your management code is: {registration.management_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[registration.user.email],
                html_message=f'''
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px;">
                    <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; color: white;">
                        <h2 style="color: #ffffff; margin: 0; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">Magic Events</h2>
                        <h3 style="color: #f0f0f0; margin: 10px 0 0 0; font-weight: normal;">Registration Confirmation</h3>
                    </div>
                    <div style="background: #f8fafc; padding: 25px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="color: #2d3748; margin-bottom: 15px; font-size: 20px; border-bottom: 2px solid #4299e1; padding-bottom: 10px;">Event: {registration.event.title}</h4>
                        <div style="color: #4a5568; line-height: 1.6;">
                            <p style="margin: 8px 0;"><strong style="color: #2d3748;">Start Date:</strong> {registration.event.start_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                            <p style="margin: 8px 0;"><strong style="color: #2d3748;">End Date:</strong> {registration.event.end_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                        </div>
                    </div>
                    <div style="background: #f8fafc; padding: 30px; border-radius: 8px; text-align: center; border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <p style="font-size: 18px; margin-bottom: 25px; color: #2d3748; font-weight: 500;">Your management code is:</p>
                        <div style="font-size: 20px; font-weight: bold; color: #1a202c; padding: 20px; background: #ffffff; border: 3px solid #4299e1; border-radius: 8px; margin: 25px 0; word-break: break-all; box-shadow: 0 4px 6px rgba(0,0,0,0.1); font-family: monospace;">
                            {registration.management_code}
                        </div>
                        <p style="font-size: 16px; color: #4a5568; margin: 20px 0; font-weight: 500;">
                            Save this code! You'll need it to view or cancel your registration.
                        </p>
                    </div>
                    <div style="text-align: center; margin-top: 30px; padding: 20px; background: #edf2f7; border-radius: 8px;">
                        <p style="font-size: 14px; color: #718096; margin: 0;">
                            You can manage your registration at any time using this code.
                        </p>
                    </div>
                </div>
                '''
            )
            email_sent = True
        except Exception as e:
            pass

        response_serializer = RegistrationSerializer(registration, context={'request': request})
        response_message = 'Registration successful! Please save your management code.'
        if email_sent:
            response_message += ' A confirmation email with your management code has been sent to your email address.'

        return Response(
            {
                'message': response_message,
                'registration': response_serializer.data,
                'email_sent': email_sent
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def my(self, request):
        """get last 3 registrations for the current user"""
        registrations = Registration.objects.filter(user=request.user).order_by('-created_at')[:3]
        serializer = RegistrationManagementSerializer(registrations, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='lookup/(?P<management_code>[^/.]+)')
    def lookup(self, request, management_code=None):
        """find registration by management code"""
        registration = get_object_or_404(
            Registration,
            management_code=management_code,
            user=request.user
        )
        serializer = RegistrationManagementSerializer(registration, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='cancel/(?P<management_code>[^/.]+)')
    def cancel(self, request, management_code=None):
        """cancel registration by management code"""
        registration = get_object_or_404(
            Registration,
            management_code=management_code,
            user=request.user
        )

        if registration.status == 'cancelled':
            return Response(
                {'error': 'Registration is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not registration.can_cancel():
            return Response(
                {
                    'error': 'Cannot cancel this registration',
                    'reason': 'Cancellation is only allowed for events lasting no more than 2 days and at least 2 days before the event starts'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        registration.cancel()
        serializer = RegistrationManagementSerializer(registration, context={'request': request})

        return Response(
            {
                'message': 'Registration cancelled successfully',
                'registration': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @method_decorator(login_required)
    @action(detail=False, methods=['get'], url_path='ui/manage')
    def management_ui(self, request):
        """web UI for registration management"""
        return render(request, 'events/registration_management.html')