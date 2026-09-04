from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Redirects incoming visitors to the appropriate dashboard or login screen
def index_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'trainee':
            return redirect('trainee_dashboard')
        return redirect('trainer_dashboard')
    return redirect('login_page')


# Renders the Field Atlas login screen with dual identifier support
def login_page(request):
    if request.user.is_authenticated:
        return redirect('index_view')
    return render(request, 'auth/login.html')


# Renders the new user registration screen with role selection
def register_page(request):
    if request.user.is_authenticated:
        return redirect('index_view')
    return render(request, 'auth/register.html')


# Renders the 6-digit email OTP verification page
def verify_otp_page(request):
    return render(request, 'auth/verify_otp.html')


# Renders the password recovery request interface
def forgot_password_page(request):
    return render(request, 'auth/forgot_password.html')


# Renders the comprehensive multi-view dashboard for trainers and coordinators
@login_required(login_url='login_page')
def trainer_dashboard_page(request):
    if request.user.role == 'trainee':
        messages.warning(request, "Access restricted. Redirecting to your trainee portal.")
        return redirect('trainee_dashboard')
    return render(request, 'trainer/dashboard.html', {'user': request.user})


# Renders the learner-centric personal progress and check-in portal
@login_required(login_url='login_page')
def trainee_dashboard_page(request):
    if request.user.role == 'trainer' and not request.user.is_superuser:
        messages.warning(request, "Access restricted. Redirecting to your trainer portal.")
        return redirect('trainer_dashboard')
    return render(request, 'trainee/dashboard.html', {'user': request.user})


# Renders the editable profile management page for all user roles
@login_required(login_url='login_page')
def profile_page(request):
    return render(request, 'profile.html', {'user': request.user})
