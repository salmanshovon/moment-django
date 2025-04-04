import smtplib
from django.core.mail.backends.smtp import EmailBackend

class CustomSMTPBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        
        try:
            self.connection = smtplib.SMTP_SSL(self.host, self.port)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            print(f"SMTP connection failed: {e}")
            raise