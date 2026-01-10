import resend
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class ResendApiBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        
        resend.api_key = settings.RESEND_API_KEY
        sent_count = 0
        
        for message in email_messages:
            try:
                params = {
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": message.to,
                    "subject": message.subject,
                    "html": message.body,
                }
                resend.Emails.send(params)
                sent_count += 1
            except Exception as e:
                print(f"Error sending via Resend API: {e}")
        return sent_count