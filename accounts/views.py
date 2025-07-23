from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
import json
import random
import string
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .forms import CustomUserCreationForm
from django.contrib.auth import login as django_login

class AuthViewSet(viewsets.ViewSet):
    """AuthViewSet handles user authentication and registration"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get', 'post'], url_path='login')
    def login(self, request):
        if request.method == 'GET':
            return render(request, 'accounts/login.html')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            django_login(request, user)
            print(f"User {user.username} logged in")
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'accounts/login.html')

    @action(detail=False, methods=['get', 'post'], url_path='signup')
    def signup(self, request):
        if request.method == 'GET':
            form = CustomUserCreationForm()
            return render(request, 'accounts/signup.html', {'form': form})
        
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            verified_emails = request.session.get('verified_emails', [])
            
            if email not in verified_emails:
                messages.error(request, 'Please verify your email before creating account.')
                return render(request, 'accounts/signup.html', {'form': form})
            
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = email
            user.save()
            
            request.session.pop('verified_emails', None)
            request.session.pop('verification_codes', None)
            
            from django.contrib.auth import login as django_login
            django_login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('/')
        
        return render(request, 'accounts/signup.html', {'form': form})

    @action(detail=False, methods=['get', 'post'], url_path='logout')
    def logout(self, request):
        logout(request)
        return redirect('/')

class ProfileViewSet(viewsets.ViewSet):
    """ProfileViewSet handles user profile management"""
    permission_classes = [IsAuthenticated]

    @method_decorator(login_required)
    def list(self, request):
        """display user profile"""
        return render(request, 'accounts/profile.html')

    @action(detail=False, methods=['post'], url_path='update')
    def update_profile(self, request):
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        messages.success(request, 'Your profile was successfully updated!')
        return redirect('accounts:profile-list')

    @action(detail=False, methods=['get', 'post'], url_path='password-change')
    def password_change(self, request):
        if request.method == 'GET':
            form = PasswordChangeForm(request.user)
            return render(request, 'accounts/password_change.html', {'form': form})
        
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile-list')
        
        for error in form.errors.values():
            messages.error(request, error)
        return render(request, 'accounts/password_change.html', {'form': form})


class VerificationViewSet(viewsets.ViewSet):
    """VerificationViewSet handles email verifications"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='send-code')
    def send_verification_code(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({'success': False, 'message': 'Email is required'})
            
            code = self.generate_verification_code()
            
            if 'verification_codes' not in request.session:
                request.session['verification_codes'] = {}
            
            request.session['verification_codes'][email] = code
            request.session.modified = True
            
            try:
                send_mail(
                    subject='Magic Events - Email Verification Code',
                    message=f'Your verification code is: {code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=f'''
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px;">
                        <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; color: white;">
                            <h2 style="color: #ffffff; margin: 0; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">Magic Events</h2>
                            <h3 style="color: #f0f0f0; margin: 10px 0 0 0; font-weight: normal;">Email Verification</h3>
                        </div>
                        <div style="background: #f8fafc; padding: 30px; border-radius: 8px; text-align: center; border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <p style="font-size: 18px; margin-bottom: 25px; color: #2d3748; font-weight: 500;">Your verification code is:</p>
                            <div style="font-size: 36px; font-weight: bold; color: #1a202c; letter-spacing: 8px; margin: 25px 0; padding: 20px; background: #ffffff; border: 3px solid #4299e1; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                {code}
                            </div>
                            <p style="font-size: 14px; color: #718096; margin-top: 20px;">
                                This code will expire soon. Please use it to complete your registration.
                            </p>
                        </div>
                    </div>
                    '''
                )
                return JsonResponse({'success': True, 'message': 'Verification code sent'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Failed to send email'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Server error'})

    @action(detail=False, methods=['post'], url_path='verify-code')
    def verify_email_code(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            code = data.get('code', '').strip()
            
            if not email or not code:
                return JsonResponse({'success': False, 'message': 'Email and code required'})
            
            stored_codes = request.session.get('verification_codes', {})
            
            if email not in stored_codes or stored_codes[email] != code:
                return JsonResponse({'success': False, 'message': 'Invalid verification code'})
            
            if 'verified_emails' not in request.session:
                request.session['verified_emails'] = []
            
            if email not in request.session['verified_emails']:
                request.session['verified_emails'].append(email)
            
            request.session.modified = True
            
            return JsonResponse({'success': True, 'message': 'Email verified successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Server error'})

    def generate_verification_code(self):
        return ''.join(random.choices(string.digits, k=6))


class ValidationViewSet(viewsets.ViewSet):
    """ValidationViewSet handles username and email validation"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='check-username')
    def check_username(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            
            if not username:
                return JsonResponse({'exists': False})
            
            exists = User.objects.filter(username=username).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'exists': False, 'error': 'Server error'})

    @action(detail=False, methods=['post'], url_path='check-email')
    def check_email(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({'exists': False})
            
            exists = User.objects.filter(email=email).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'exists': False, 'error': 'Server error'})