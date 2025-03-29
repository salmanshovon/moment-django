import random
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from ipware import get_client_ip


def generate_otp(user):
    otp = str(random.randint(100000, 999999))
    user.profile.otp = otp
    user.profile.otp_created_at = timezone.now()
    user.profile.save()
    return otp


def send_email_otp(user):
    otp = generate_otp(user)  # Assuming this function generates the OTP

    # Define the HTML template for the email
    html_message = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background-color: #007bff;
                color: #ffffff;
                padding: 20px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                padding: 20px;
                color: #333333;
                line-height: 1.6;
            }}
            .otp-code {{
                font-size: 28px;
                font-weight: bold;
                color: #007bff;
                text-align: center;
                margin: 20px 0;
                padding: 10px;
                background-color: #e9f5ff;
                border-radius: 4px;
                display: inline-block;
                width: 100%;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #777777;
                background-color: #f4f4f4;
            }}
            .footer a {{
                color: #007bff;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                OTP Verification
            </div>
            <div class="content">
                <p>Dear {user.username},</p>
                <p>Your One-Time Password (OTP) for account verification is:</p>
                <div class="otp-code">
                    {otp}
                </div>
                <p>Please use this OTP to complete your verification process for Aranya IT services. This OTP is valid for 10 minutes only and should not be shared with anyone.</p>
                <p>If you did not request this OTP, please ignore this message or contact our support team immediately.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Aranya Info-Tech. All rights reserved.</p>
                <p><a href="https://www.aranyait.com.bd">Visit Aranya IT</a> for more information.</p>
            </div>
        </div>
    </body>
    </html>
    '''

    # Plain text fallback for email clients that don't support HTML
    plain_message = f'Your OTP for account verification is: {otp}'

    # Send the email
    send_mail(
        subject='Account Verification',
        message=plain_message,  # Plain text version
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        html_message=html_message,  # HTML version
    )
   

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


def get_timezone_from_ip(request):
    """
    Get user's timezone from their IP address using GeoIP2.
    """
    ip, is_routable = get_client_ip(request)  # Extract user IP
    if ip is None:
        return None  # No IP found


    try:
        geo = GeoIP2()
        timezone = geo.city(ip).get("time_zone")
        return timezone
    except Exception as e:
        return None  # GeoIP lookup failed


