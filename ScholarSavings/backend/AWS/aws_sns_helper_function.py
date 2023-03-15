# This is a helper function that sending the POST request with the user's email, token,... to AWS SNS in order to send the user's the confirmation email or sms message
# import libraries
import boto3
import os
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Api, Resource, reqparse

# import from another folders
from database.users_models import db, Registration

aws_sns_app = Flask(__name__)
aws_sns_app.config['SERVER_NAME'] = 'localhost:5000'
aws_sns_app.config['APPLICATION_ROOT'] = '/'
aws_sns_app.config['PREFERRED_URL_SCHEME'] = 'http'
aws_sns_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# configure the app to work with boto3 AWS SNS Service
aws_sns_app.config['SECRET_KEY'] =  'SWEAWS2302'
aws_sns_app.config['CONFIRMATION_TOKEN_EXPIRATION'] = 900 # 15 minutes
sns_client = boto3.client('sns', region_name='us-east-1')

# database connection
aws_sns_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'

db.init_app(aws_sns_app)
api = Api(aws_sns_app)

class AWS_SNS_SDKs_setup(Resource):
 def __init__(self) -> None:
  with aws_sns_app.app_context():
   super().__init__()

 # function sending an email confirmation using AWS SDKs + boto3
 def send_email_confirmation(self, email):
  with aws_sns_app.app_context():
   # Generate a random JWT Token with expiration time of 15 minutes
   expiration_time = datetime.utcnow() + timedelta(seconds=aws_sns_app.config['CONFIRMATION_TOKEN_EXPIRATION'])
   payload = {
    'email' : email,
    'exp' : expiration_time
   }

   token = jwt.encode(payload, aws_sns_app.config['SECRET_KEY'], algorithm='HS256')
   # decode the token to string object to store into the database along with the user's email
   # decoded_token = token.decode('utf-8')

   # store the decoded_token into the user database
   row = Registration.query.filter_by(verification_method=email).first()
   try:
    if row:
     row.aws_token = token
     db.session.commit()

     # Send confirmation message to email
     email_subject = 'Confirm your account!'
     email_body = f'Please click on the link below to confirm your account:\n\n{request.host_url}confirm-email?token={token}\n\nThis confirmation email link will be expired in 15 minutes.'
     email_message = {
      'Subject' : {'Data': email_subject},
      'Body' : {'Text': {'Data': email_body}},
      'Destination' : {'ToAddresses' : [email]}
     }
     sns_client.publish(Message=email_body, TopicArn=os.environ.get('AWS_SNS_EMAIL_TOPIC'))

     return jsonify({'message' : 'Confirmation message sent to this email successfully!'}), 200

    else:
     return {'error' : 'User not found in the database'}, 404
    
   except SQLAlchemyError as e:
    db.session.rollback()
    return {'error': str(e)}, 500
  
 # function send an sms confirmation using AWS SDKs + boto3
 def send_sms_confirmation(self, phone_number):
  with aws_sns_app.app_context():
   # Generate a random JWT Token with expiration time of 15 minutes
   expiration_time = datetime.utcnow() + timedelta(seconds=aws_sns_app.config['CONFIRMATION_TOKEN_EXPIRATION'])
   payload = {
    'phone_number' : phone_number,
    'exp' : expiration_time
   }
   token = jwt.encode(payload, aws_sns_app.config['SECRET_KEY'], algorithm='HS256')
   # decode the token and store it into the database
   # decoded_token = token.decode('utf-8')

   # query the database to find the user with the phone number
   row = Registration.query.filter_by(verification_method=phone_number).first()

   try:
    if row: 
     # store the decoded token into the database
     row.aws_token = token
     db.session.commit()

     # Send SMS confirmation to the phone number
     sms_body = f'Please click the link below to confirm your account:\n{request.host_url}confirm-sms?token={token}\nThis SMS confirmation link will be expired in 15 minutes.'
     sns_client.publish(Message=sms_body, PhoneNumber=phone_number)

     return jsonify({'message' : 'Confirmation message sent to this phone number successfully!'}), 200
    
    else:
     return jsonify({'error' : 'User not found in the database!'}), 404
    
   except SQLAlchemyError as e:
    return jsonify({'error' : str(e)}), 500

# Resource to handle the email confirm request
class Email_Confirmation(Resource):
 def __init__(self) -> None:
  with aws_sns_app.app_context():
   super().__init__()

 # function to handle the email confirmation action GET request
 def confirm_email(self):
  with aws_sns_app.app_context():
   # get the token value
   token = request.args.get('token')
   try:
    # get the message
    # encrypted the token using hash256 algorithm
    payload = jwt.decode(token, aws_sns_app.config['SECRET_KEY'], algorithm='HS256')
   # if the token is expired
   except jwt.ExpiredSignatureError:
    return jsonify({'error' : 'Token has expired.'}), 401
   # if the token is invalid
   except jwt.InvalidTokenError:
    return jsonify({'error' : 'Invalid token.'}), 401

   email = payload['email']

   # Update user account to mark account as verified
   # query the registration database with the 'account_verified' column
   user = Registration.query.filter(Registration.email == email).first()

   # update the value at 'account_verified' column
   user.account_verified = True

   # commit the change to the database
   db.session.commit()

   # later on, fix this to render a email_confirmation template
   return jsonify({'message' : 'Email is confirmed'}), 200

# Resource to handle sms confirm request
class SMS_Confirmation(Resource):
 def __init__(self) -> None:
  with aws_sns_app.app_context():
   super().__init__()

 # function to handle the sms confirmation GET request
 def confirm_sms(self):
  with aws_sns_app.app_context():
   token = request.args.get('token')
   try:
    # get the sms message
    # encrypted the token using HASH256 Algorithm
    payload = jwt.decode(token, aws_sns_app.config['SECRET_KEY'], algorithm='HS256')
   # if the token is expired
   except jwt.ExpiredSignatureError:
    return jsonify({'error' : 'Token has expired.'}), 401
   # if the token is invalid
   except jwt.InvalidTokenError:
    return jsonify({'error' : 'Token is invalid'}), 401

   phone_number = payload['phone_number']

   # Update user account to mark account as verified
   # query the registration database with the 'account_verified' column
   user = Registration.query.filter(Registration.email == phone_number).first()

   # update the value at 'account_verified' column
   user.account_verified = True

   # commit the change to the database
   db.session.commit()

   # later on, fix this to render a sms_confirmation template
   return jsonify({'message' : 'Phone number is confirmed'}), 200

# add all the resources to the rest api
api.add_resource(AWS_SNS_SDKs_setup, '/scholarsavings/createaccount/')
api.add_resource(Email_Confirmation, '/scholarsavings/confirm/email/')
api.add_resource(SMS_Confirmation, '/scholarsavings/confirm/sms/')