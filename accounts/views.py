from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
import json
import random
import string
from django.http import JsonResponse


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomSignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}! You can now log in.')
        return response


class CustomLogoutView(LogoutView):
    next_page = '/'


@login_required
def profile_view(request):
    if request.method == 'POST':
        # Handle profile info update
        if 'first_name' in request.POST:
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('accounts:profile')
        
        # Handle password change
        elif 'old_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('accounts:profile')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully changed!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Check if email is verified in session
            email = form.cleaned_data['email'].lower()
            verified_emails = request.session.get('verified_emails', [])
            
            if email not in verified_emails:
                messages.error(request, 'Please verify your email before creating account.')
                return render(request, 'registration/signup.html', {'form': form})
            
            # Create user
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = email
            user.save()
            
            # Clean up session
            request.session.pop('verified_emails', None)
            request.session.pop('verification_codes', None)
            
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')  # Change to your home URL
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@require_http_methods(["POST"])
def send_verification_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Generate and store code in session
        code = generate_verification_code()
        
        if 'verification_codes' not in request.session:
            request.session['verification_codes'] = {}
        
        request.session['verification_codes'][email] = code
        request.session.modified = True
        
        # Send email
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

@require_http_methods(["POST"])
def verify_email_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        code = data.get('code', '').strip()
        
        if not email or not code:
            return JsonResponse({'success': False, 'message': 'Email and code required'})
        
        # Check code in session
        stored_codes = request.session.get('verification_codes', {})
        
        if email not in stored_codes or stored_codes[email] != code:
            return JsonResponse({'success': False, 'message': 'Invalid verification code'})
        
        # Mark email as verified
        if 'verified_emails' not in request.session:
            request.session['verified_emails'] = []
        
        if email not in request.session['verified_emails']:
            request.session['verified_emails'].append(email)
        
        request.session.modified = True
        
        return JsonResponse({'success': True, 'message': 'Email verified successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Server error'})

@require_http_methods(["POST"])
def check_username(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({'exists': False})
        
        # Check if username exists
        exists = User.objects.filter(username=username).exists()
        
        return JsonResponse({'exists': exists})
        
    except Exception as e:
        return JsonResponse({'exists': False, 'error': 'Server error'})

@require_http_methods(["POST"])
def check_email(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'exists': False})
        
        # Check if email exists
        exists = User.objects.filter(email=email).exists()
        
        return JsonResponse({'exists': exists})
        
    except Exception as e:
        return JsonResponse({'exists': False, 'error': 'Server error'})