import random
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def generate_otp(user):
    otp = str(random.randint(100000, 999999))
    user.profile.otp = otp
    user.profile.otp_created_at = timezone.now()
    user.profile.save()
    return otp

def send_email_otp(user):
    otp = generate_otp(user)
    # Send otp to user's email
    subject = 'Account Verification'
    message = f'Your OTP is {otp}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
   

def verify_otp(user, otp):
    if user.profile.otp == otp and (timezone.now() - user.profile.otp_created_at).seconds < 600:
        user.profile.is_verified = True
        user.profile.save()
        return True
    return False

def update_password(user, password):
    user.set_password(password)
    user.save()
    return True

# @csrf_exempt

