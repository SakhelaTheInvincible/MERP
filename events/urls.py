from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/events/', views.EventListView.as_view(), name='api-events-list'),
    path('api/events/upcoming/', views.UpcomingEventsView.as_view(), name='api-events-upcoming'),
    path('api/events/past/', views.PastEventsView.as_view(), name='api-events-past'),
    path('api/events/create/', views.EventCreateView.as_view(), name='api-event-create'),
    path('api/events/<int:pk>/', views.EventDetailView.as_view(), name='api-event-detail'),
    path('api/registrations/', views.RegistrationCreateView.as_view(), name='api-registration-create'),
    path('api/registrations/my/', views.my_registrations, name='api-my-registrations'),
    path('api/registrations/<uuid:management_code>/', views.registration_lookup, name='api-registration-lookup'),
    path('api/registrations/<uuid:management_code>/cancel/', views.cancel_registration, name='api-registration-cancel'),
    
    # UI endpoints
    path('', views.events_list_ui, name='events-list'),
    path('create/', views.event_create_ui, name='event-create'),
    path('events/<int:event_id>/', views.event_detail_ui, name='event-detail'),
    path('manage/', views.registration_management_ui, name='registration-management'),
] 