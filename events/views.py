from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Event, Registration
from .serializers import (
    EventSerializer, EventCreateSerializer, RegistrationCreateSerializer, 
    RegistrationSerializer, RegistrationManagementSerializer
)


class EventCreateView(generics.CreateAPIView):
    """Create a new event"""
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        
        # Return event details
        response_serializer = EventSerializer(event)
        return Response(
            {
                'message': 'Event created successfully!',
                'event': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class EventListView(generics.ListAPIView):
    """List all events - deprecated, use UpcomingEventsView or PastEventsView instead"""
    serializer_class = EventSerializer
    
    def get_queryset(self):
        # Show all events for now (can be filtered later if needed)
        return Event.objects.all().order_by('start_date')


class UpcomingEventsView(generics.ListAPIView):
    """List all upcoming events (end date is in the future)"""
    serializer_class = EventSerializer
    
    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(end_date__gt=now).order_by('start_date')


class PastEventsView(generics.ListAPIView):
    """List all past events (end date is in the past)"""
    serializer_class = EventSerializer
    
    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(end_date__lte=now).order_by('-end_date')


class EventDetailView(generics.RetrieveAPIView):
    """Get details of a specific event"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class RegistrationCreateView(generics.CreateAPIView):
    """Create a new registration for an event"""
    serializer_class = RegistrationCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()
        
        # Return registration details with management code
        response_serializer = RegistrationSerializer(registration)
        return Response(
            {
                'message': 'Registration successful! Please save your management code.',
                'registration': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
def registration_lookup(request, management_code):
    """Look up registration by management code - only for the current user"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Only allow users to look up their own registrations
        registration = get_object_or_404(
            Registration, 
            management_code=management_code,
            user=request.user
        )
        serializer = RegistrationManagementSerializer(registration)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': 'Registration not found or you do not have permission to access it'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def cancel_registration(request, management_code):
    """Cancel a registration using management code - only for the current user"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Only allow users to cancel their own registrations
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
        serializer = RegistrationManagementSerializer(registration)
        
        return Response(
            {
                'message': 'Registration cancelled successfully',
                'registration': serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {'error': 'Unable to cancel registration or you do not have permission'},
            status=status.HTTP_400_BAD_REQUEST
        )


# UI Views (for basic web interface)
from django.shortcuts import render
from django.http import JsonResponse


def events_list_ui(request):
    """Basic web interface for listing events"""
    return render(request, 'events/events_list.html')


def event_detail_ui(request, event_id):
    """Basic web interface for event details and registration"""
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


@api_view(['GET'])
def my_registrations(request):
    """Get all registrations for the current user"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    registrations = Registration.objects.filter(user=request.user).order_by('-created_at')[:3]
    serializer = RegistrationManagementSerializer(registrations, many=True)
    return Response(serializer.data)


@login_required
def registration_management_ui(request):
    """Basic web interface for registration management - requires login"""
    return render(request, 'events/registration_management.html')


@login_required
def event_create_ui(request):
    """Basic web interface for creating events"""
    return render(request, 'events/event_create.html') 