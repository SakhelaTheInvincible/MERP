from rest_framework import serializers
from .models import Event, Registration


class EventCreateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')
    end_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'end_date', 'thumbnail']
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "Start date must be before end date"
                )
        return data


class EventSerializer(serializers.ModelSerializer):
    duration_days = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    can_register = serializers.ReadOnlyField()
    registration_count = serializers.SerializerMethodField()
    start_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')
    end_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date', 
            'thumbnail', 'duration_days', 'is_upcoming', 'can_register',
            'registration_count', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_registration_count(self, obj):
        return obj.registrations.filter(status='active').count()


class RegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['event', 'phone']

    def validate(self, data):
        event = data.get('event')
        user = self.context['request'].user
        
        if not event.can_register:
            raise serializers.ValidationError(
                "Cannot register for events that have already started"
            )
        
        if Registration.objects.filter(event=event, user=user, status='active').exists():
            raise serializers.ValidationError(
                "You are already registered for this event"
            )
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        event = validated_data['event']
        
        # check if there's an existing cancelation
        existing_registration = Registration.objects.filter(
            event=event, 
            user=user, 
            status='cancelled'
        ).first()
        
        if existing_registration:
            # reactivate the cancelled registration
            existing_registration.phone = validated_data.get('phone', existing_registration.phone)
            existing_registration.reactivate()
            return existing_registration
        else:
            # or just create a new registration
            validated_data['user'] = user
            return super().create(validated_data)


class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    can_cancel = serializers.ReadOnlyField()

    class Meta:
        model = Registration
        fields = [
            'id', 'event', 'full_name', 'email', 'phone', 
            'management_code', 'status', 'can_cancel', 
            'created_at', 'cancelled_at'
        ]
        read_only_fields = [
            'management_code', 'status', 'created_at', 'cancelled_at'
        ]


class RegistrationManagementSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    can_cancel = serializers.ReadOnlyField()

    class Meta:
        model = Registration
        fields = [
            'id', 'event', 'full_name', 'email', 'phone', 
            'status', 'can_cancel', 'created_at', 'cancelled_at'
        ]
        read_only_fields = ['email', 'phone', 'created_at', 'cancelled_at'] 