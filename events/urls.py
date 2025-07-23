from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/events', views.EventViewSet, basename='event')
router.register(r'api/registrations', views.RegistrationViewSet, basename='registration')

urlpatterns = [
    # UI endpoints
    path('', views.EventViewSet.as_view({'get': 'list_ui'}), name='events-list'),
    path('create/', views.EventViewSet.as_view({'get': 'create_ui'}), name='event-create'),
    path('events/<int:pk>/', views.EventViewSet.as_view({'get': 'detail_ui'}), name='event-detail'),
    path('manage/', views.RegistrationViewSet.as_view({'get': 'management_ui'}), name='registration-management'),
    
    # API routes
    path('', include(router.urls)),
]