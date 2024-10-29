from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import User

@login_required
def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Generate verification token
            token = get_random_string(64)
            user.verification_token = token
            user.save()

            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', args=[token])
            )
            
            subject = 'Verify your email address'
            message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'verification_url': verification_url,
            })
            
            send_mail(
                subject,
                message,
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 
                'Registration successful. Please check your email to verify your account.')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        if not user.is_verified:
            user.is_verified = True
            user.verification_token = ''
            user.save()
            messages.success(request, 'Email verified successfully. You can now log in.')
        else:
            messages.info(request, 'Email already verified.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
    
    return redirect('accounts:login')