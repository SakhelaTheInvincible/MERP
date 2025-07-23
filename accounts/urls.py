from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'verification', views.VerificationViewSet, basename='verification')
router.register(r'validation', views.ValidationViewSet, basename='validation')

urlpatterns = [
    path('', include(router.urls)),
]