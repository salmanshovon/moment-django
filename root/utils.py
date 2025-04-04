from django.core.mail import EmailMessage
from smtplib import SMTPException

def send_contact_email_to_admin(name, email, message):
    """Returns (success: bool, error_message: str)"""
    try:
        msg = EmailMessage(
            subject=f"New Contact Message from {name} ({email})",
            body=message,
            from_email=email,
            to=["admin@aranyait.com.bd"],
            reply_to=[email],
        )
        msg.send()
        return True, None
    except SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"