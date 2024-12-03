from celery import Celery
from src.mail import create_message, mail
from asgiref.sync import async_to_sync
from pydantic import EmailStr
import logging

c_app = Celery()

# Add Config File
c_app.config_from_object("src.config")


# Add Send Mail Celery Task
@c_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_bg_email(self, recipients: list[EmailStr], subject: str, body: str):
    try:
        # Create the message
        message = create_message(recipients=recipients, subject=subject, body=body)

        # Send the message synchronously
        async_to_sync(mail.send_message)(message)

        print("EMAIL SENT")
    except Exception as e:
        logging.warning(f"Error in Sending Background Mail: {str(e)}")
