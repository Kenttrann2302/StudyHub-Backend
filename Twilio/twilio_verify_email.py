# this is a function using Twilio SendGrid Service to verify the user's email after the user click on the verify email button in the email template
import os
from twilio.rest import Client

# function using TWILIO API to handle email verification 
def verify_email(email_id, twilio_code):
 # get the account sid and auth token for Twilio SendGrid service from the env
 account_sid = os.environ['TWILIO_ACCOUNT_SID']
 auth_token = os.environ['TWILIO_AUTH_TOKEN']
 service_sid = os.environ['TWILIO_SERVICE_SID']

 # create a client
 client = Client(account_sid, auth_token)

 verification_check = client.verify \
                            .v2 \
                            .services(service_sid) \
                            .verification_checks \
                            .create(to=email_id, code=twilio_code)
 
 return verification_check
