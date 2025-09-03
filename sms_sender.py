# sms_sender.py
import os
from twilio.rest import Client

ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]  # e.g. +1415xxxxxxx

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(message, to_number):
    # ensure E.164 like +91987xxxxxxx
    if not to_number.startswith("+"):
        raise ValueError("Phone must be in E.164 format, e.g. +919876543210")
    client.messages.create(body=message, from_=TWILIO_NUMBER, to=to_number)
