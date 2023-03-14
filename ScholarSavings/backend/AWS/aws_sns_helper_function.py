# This is a helper function that sending the POST request with the user's email, token,... to AWS SNS in order to send the user's the confirmation email or sms message
# import libraries
import boto3
import os
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from register import register_app, api, sns_client, db

class AWS_SNS_SDKs_setup(Resource):
 def __init__(self, email, phone_number) -> None:
  with register_app.app_context():
   self.email = email
   self.phone_number = phone_number

 # function sending an email confirmation using AWS SDKs + boto3
 def send_email_confirmation(self):
  with register_app.app_context():
   # Generate a random JWT Token with expiration time of 15 minutes
   expiration_time = datetime.utcnow() + timedelta(seconds=register_app.config['CONFIRMATION_TOKEN_EXPIRATION'])
   payload = {
    'email' : self.email,
    'exp' : expiration_time
   }

   token = jwt.encode(payload, register_app.config['SECRET_KEY'])
   # decode the token to string object to store into the database along with the user's email
   decoded_token = token.decode('utf-8')

   

   # Send confirmation message to email
   email_subject = 'Confirm your account!'
   email_body = f'Please click on the link below to confirm your account:\n\n{request.host_url}confirm-email?token={token.decode()}\n\nThis confirmation email link will be expired in 15 minutes.'
   email_message = {
    'Subject' : {'Data': email_subject},
    'Body' : {'Text': {'Data': email_body}},
    'Destination' : {'ToAddresses' : [self.email]}
   }
   sns_client.publish(Message=email_body, TopicArn=os.environ.get('AWS_SNS_EMAIL_TOPIC'))

   return jsonify({'message' : 'Confirmation message sent to this email successfully!'}), 200

 # function send an sms confirmation using AWS SDKs + boto3
 def send_sms_confirmation(self):
  with register_app.app_context():
   # Generate a random JWT Token with expiration time of 15 minutes
   expiration_time = datetime.utcnow() + timedelta(seconds=register_app.config['CONFIRMATION_TOKEN_EXPIRATION'])
   payload = {
    'phone_number' : self.phone_number,
    'exp' : expiration_time
   }
   token = jwt.encode(payload, register_app.config['SECRET_KEY'])

   # Send SMS confirmation to the phone number
   sms_body = f'Please click the link below to confirm your account:\n{request.host_url}confirm-sms?token={token.decode()}\nThis SMS confirmation link will be expired in 15 minutes.'
   sns_client.publish(Message=sms_body, PhoneNumber=self.phone_number)

   return jsonify({'message' : 'Confirmation message sent to this phone number successfully!'}), 200

# Resource to handle the email confirm request
class Email_Confirmation(Resource):
 def __init__(self, registration_table) -> None:
  with register_app.app_context():
   self.registration_table = registration_table

 # function to handle the email confirmation action GET request
 def confirm_email(self):
  with register_app.app_context():
   # get the token value
   token = request.args.get('token')
   try:
    # get the message
    # encrypted the token using hash256 algorithm
    payload = jwt.decode(token, register_app.config['SECRET_KEY'], algorithms=['HS256'])
   # if the token is expired
   except jwt.ExpiredSignatureError:
    return jsonify({'error' : 'Token has expired.'}), 401
   # if the token is invalid
   except jwt.InvalidTokenError:
    return jsonify({'error' : 'Invalid token.'}), 401

   email = payload['email']

   # Update user account to mark account as verified
   # query the registration database with the 'account_verified' column
   user = self.registration_table.query.filter(self.registration_table.email == email).first()

   # update the value at 'account_verified' column
   user.account_verified = True

   # commit the change to the database
   db.session.commit()

   # later on, fix this to render a email_confirmation template
   return jsonify({'message' : 'Email is confirmed'}), 200

# Resource to handle sms confirm request
class SMS_Confirmation(Resource):
 def __init__(self, registration_table) -> None:
  with register_app.app_context():
   self.registration_table = registration_table

 # function to handle the sms confirmation GET request
 def confirm_sms(self):
  with register_app.app_context():
   token = request.args.get('token')
   try:
    # get the sms message
    # encrypted the token using HASH256 Algorithm
    payload = jwt.decode(token, register_app.config['SECRET_KEY'], algorithms=['HS256'])
   # if the token is expired
   except jwt.ExpiredSignatureError:
    return jsonify({'error' : 'Token has expired.'}), 401
   # if the token is invalid
   except jwt.InvalidTokenError:
    return jsonify({'error' : 'Token is invalid'}), 401

   phone_number = payload['phone_number']

   # Update user account to mark account as verified
   # query the registration database with the 'account_verified' column
   user = self.registration_table.query.filter(self.registration_table.email == phone_number).first()

   # update the value at 'account_verified' column
   user.account_verified = True

   # commit the change to the database
   db.session.commit()

   # later on, fix this to render a sms_confirmation template
   return jsonify({'message' : 'Phone number is confirmed'}), 200

# add all the resources to the rest api
api.add_resource(AWS_SNS_SDKs_setup, '/scholarsavings/createaccount/')
api.add_resource(Email_Confirmation, '/scholarsavings/confirm/email/')
api.add_resource()