# This is a helper function that sending the POST request with the user's email, token,... to AWS SNS in order to send the user's the confirmation email or sms message
# import libraries
import boto3
import botocore
import logging
import os
import jwt
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Api, Resource, reqparse
import requests
import secrets
import string
import json
import pdb

# import from another folders
from database.users_models import db, Users
# import a granting permission helper function to grant access to users who have verified their account
from helper_functions.grant_permission import grant_permission_to_verified_users

aws_sns_app = Flask(__name__)
aws_sns_app.config['SERVER_NAME'] = 'localhost:5000'
aws_sns_app.config['APPLICATION_ROOT'] = '/'
aws_sns_app.config['PREFERRED_URL_SCHEME'] = 'http'
aws_sns_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# configure the app to work with boto3 AWS SNS Service by entering the credentials of IAM user which is given the access to AWS SNS Service
aws_sns_app.config['AWS_ACCESS_KEY_ID'] = 'AKIA4GBM4ARGVCZUNKEY'
aws_sns_app.config['AWS_SECRET_ACCESS_KEY'] =  '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'
aws_sns_app.config['AWS_DEFAULT_REGION'] = 'us-east-1'
aws_sns_app.config['CONFIRMATION_TOKEN_EXPIRATION'] = 900 # 15 minutes

# create a session with aws sns client
# session = boto3.Session(
#   aws_access_key_id = aws_sns_app.config['AWS_ACCESS_KEY_ID'],
#   aws_secret_access_key=aws_sns_app.config['AWS_SECRET_ACCESS_KEY'],
#   aws_region_name = aws_sns_app.config['AWS_REGION_NAME'],
#   aws_session_token = aws_sns_app.config['']
# )

sns_client = boto3.client('sns', region_name='us-east-1')
sns_resource = boto3.resource('sns', region_name='us-east-1')

if not os.environ.get('AWS_ACCESS_KEY_ID'):
  print('AWS_ACCESS_KEY_ID is missing!')

if not os.environ.get('AWS_SECRET_ACCESS_KEY'):
  print('AWS_SECRET_ACCESS_KEY is missing!')

if not os.environ.get('AWS_DEFAULT_REGION'):
  print('AWS_DEFAULT_REGION is missing!')

if not os.environ.get('AWS_SESSION_TOKEN'):
  print('AWS_SESSION_TOKEN is missing!')

# database connection
aws_sns_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'

db.init_app(aws_sns_app)
api = Api(aws_sns_app)

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# generate a random string for name_prefix
def generate_random_string(length):
  alphabet = string.ascii_letters + string.digits
  return ''.join(secrets.choice(alphabet) for i in range(length))

# create TopicArn to create a topic for the request
class SnsWrapper:
  # Encapsulates Amazon SNS topic and subscription functions
  def __init__(self, sns_resource) -> None:
   # :param sns_resource: A Boto3 Amazon SNS resource
   self.sns_resource = sns_resource

  def create_topic(self, name):
    '''
      Creates a notification topic.
      
      :param name : The name of the topic to create.
      :return: The newly created topic.
    '''
    try:
      # create a unique name for the topic using the combination of prefix and unique identifier
      # topic_name = f"{name_prefix}-{uuid.uuid4()}"
      topic = self.sns_resource.create_topic(Name=name)
      logger.info("Created topic %s with ARN % s.", name, topic.arn)
    except botocore.exceptions.ClientError as error:
      if error.response['Error']['Code'] == 'LimitExceededException':
        logger.warn('API call limit exceeded; backing off and retrying...')
      logger.exception("Couldn't create topic %s.", name)
      raise error
    except botocore.exceptions.ParamValidationError as error:
      raise ValueError('The parameters you provided are incorrect: {}'.format(error))
    else:
      return topic

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

   token = jwt.encode(payload, aws_sns_app.config['AWS_SECRET_ACCESS_KEY'], algorithm='HS256')
   # decode the token to string object to store into the database along with the user's email
   # decoded_token = token.decode('utf-8')

   # store the decoded_token into the user database
   row = Users.query.filter_by(verification_method=email).first()
   try:
    pdb.set_trace()
    if row:
     row.aws_token = token
     db.session.commit()

     # Send confirmation message to email
     email_subject = 'Confirm your account!'
     email_body = f'Please click on the link below to confirm your account:\n\n{request.host_url}scholarsavings/confirm-email?id={row.user_id}&token={token}\n\nThis confirmation email link will be expired in 15 minutes.'
     email_message = {
      'Subject': {'Data': email_subject},
      'Body': {'Text': {'Data':email_body}},
      'Destination': {'ToAddresses': [email]}
     }
    
     # create a SnSWrapper model
     topic_arn_model = SnsWrapper(sns_resource=sns_resource)
     sns_topic = topic_arn_model.create_topic(name='MyTopic-eEXEKdldnX-32121e0d-16c1-4a85-a478-1527818c79df')
    
     # subscribe an email endpoint to the topic

     protocol = 'email'
     response = sns_client.subscribe(
      TopicArn=sns_topic.arn,
      Protocol=protocol,
      Endpoint=email,
      ReturnSubscriptionArn=True
     )

     if response is not None:
      # send a confirmation email to the endpoint
      sns_client.publish(
        TopicArn=sns_topic.arn,
        Message=email_body
      )

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

   token = jwt.encode(payload, aws_sns_app.config['AWS_SECRET_ACCESS_KEY'], algorithm='HS256')
   # decode the token and store it into the database
   # decoded_token = token.decode('utf-8')

   # query the database to find the user with the phone number
   row = Users.query.filter_by(verification_method=phone_number).first()

   try:
    if row: 
     # store the decoded token into the database
     row.aws_token = token
     db.session.commit()

     # Send SMS confirmation to the phone number
     sms_body = f'Thank you for choosing ScholarSaving Service!\n\nPlease click the link below to verify your email with us:\n{request.host_url}scholarsavings/confirm-sms?id={row.user_id}&token={token}\nThis SMS confirmation link will be expired in 15 minutes.'

     # Send sms confirmation message to the phone number
     # create a SnSWrapper model
     topic_arn_model = SnsWrapper(sns_resource=sns_resource)
     sns_topic = topic_arn_model.create_topic(name='MyTopic-eEXEKdldnX-32121e0d-16c1-4a85-a478-1527818c79df')

     response = sns_client.subscibe(
      TopicArn=sns_topic.arn,
      Protocol='sms',
      Endpoint=phone_number,
      ReturnSubscriptionArn=True
     )
     
     if response is not None:
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
    payload = jwt.decode(token, aws_sns_app.config['AWS_SECRET_ACCESS_KEY'], algorithm='HS256')
   # if the token is expired
   except jwt.ExpiredSignatureError:
    return jsonify({'error' : 'Token has expired.'}), 401
   # if the token is invalid
   except jwt.InvalidTokenError:
    return jsonify({'error' : 'Invalid token.'}), 401

   email = payload['email']

   # Update user account to mark account as verified
   # query the registration database with the 'account_verified' column
   user = Users.query.filter_by(
    verification_method = email
   ).first()

   # update the value at 'account_verified' column
   user.account_verified = True

   # grant access for user for permission after they have verified their accounts
   permissions = ['can_view_dashboard', 'can_register_saving_challenges', 'can_use_geolocation_api']
   for permission in permissions:
    grant_permission_to_verified_users(permission_name=permission)

   # commit the change to the database
   db.session.commit()

   # later on, fix this to render a email_confirmation template
   return render_template('account_verification.html', name=user.username, verification_id=user.verification_id)

# Resource to handle sms confirm request
class SMS_Confirmation(Resource):
 def __init__(self) -> None:
  with aws_sns_app.app_context():
   super().__init__()

 # function to handle the sms confirmation GET request
 def confirm_sms(self):
   token = request.args.get('token')
   try:
    # get the sms message
    # encrypted the token using HASH256 Algorithm
    payload = jwt.decode(token, aws_sns_app.config['AWS_SECRET_ACCESS_KEY'], algorithm='HS256')
   # if the token is expired
   except jwt.ExpiredSignatureError:
    return jsonify({'error' : 'Token has expired.'}), 401
   # if the token is invalid
   except jwt.InvalidTokenError:
    return jsonify({'error' : 'Token is invalid'}), 401

   phone_number = payload['phone_number']

   # Update user account to mark account as verified
   # query the registration database with the 'account_verified' column
   user = Users.query.filter_by(
    verification_method = phone_number
   ).first()

   # update the value at 'account_verified' column
   user.account_verified = True

   # grant access for user for permission after they have verified their accounts
   permissions = ['can_view_dashboard', 'can_register_saving_challenges', 'can_use_geolocation_api']
   for permission in permissions:
    grant_permission_to_verified_users(permission_name=permission)

   # commit the change to the database
   db.session.commit()

   # later on, fix this to render a sms_confirmation template
   return render_template('account_verification.html', name=user.username, verification_id=user.verification_id)

# add all the resources to the rest api
api.add_resource(AWS_SNS_SDKs_setup, '/scholarsavings/createaccount/')
api.add_resource(Email_Confirmation, '/scholarsavings/confirm-email/')
api.add_resource(SMS_Confirmation, '/scholarsavings/confirm-sms/')