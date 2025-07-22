from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.CustomSignUpView.as_view(), name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password/change/', views.password_change_view, name='password_change'),
    path('signup/', views.signup_view, name='signup'),
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('verify-email-code/', views.verify_email_code, name='verify_email_code'),
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),
] 