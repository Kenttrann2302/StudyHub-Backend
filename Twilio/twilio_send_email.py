# this is a function using Twilio SendGrid Service in order to send the email verification towards user's email address for verification method
import os
from twilio.rest import Client

# function using TWILIO API to handle sending email confirmation to user's endpoint
def twilio_send_email(email_id):
 # get the account sid and auth token for Twilio SendGrid service from the env
 account_sid = os.environ['TWILIO_ACCOUNT_SID']
 auth_token = os.environ['TWILIO_AUTH_TOKEN']
 service_sid = os.environ['TWILIO_SERVICE_SID']
 template_id = os.environ['TWILIO_TEMPLATE_ID']

 # create a client
 client = Client(account_sid, auth_token)

 verification = client.verify \
                      .v2 \
                      .services(service_sid) \
                      .verifications \
                      .create(channel_configuration={
                       'template_id' : template_id,
                       'from' : 'studyhub2302@gmail.com',
                       'from_name' : 'StudyHub'
                      }, to=email_id, channel='email')

 return verification


