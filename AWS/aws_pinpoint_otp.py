# this is a helper function that using aws pinpoint service to send OTPs to user's email or SMS

# import libraries
from flask import Flask, json, jsonify, render_template, request, redirect, url_for
from flask_restful import Api, Resource
import hashlib
import boto3
from botocore.exceptions import ClientError
import os
import pdb

# import files
from helper_functions.grant_permission import grant_permission_to_verified_users

# aws_pinpoint_app configuration with Flask
aws_pinpoint_app = Flask(__name__)

# load in the sensitive data from .env
from dotenv import load_dotenv
# Load the configuration data from the .env file
load_dotenv()

# get the database connection information
database_type = os.getenv("DB_TYPE")
database_host = os.getenv("DB_HOST")
database_username = os.getenv("DB_USER")
database_password = os.getenv("DB_PASS")
database_port = os.getenv("PORT")
database_name = os.getenv("DB_NAME")

# get the aws configuration
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_default_region = os.getenv('AWS_DEFAULT_REGION')
aws_confirmation_token_expiration = os.getenv('CONFIRMATION_TOKEN_EXPIRATION')
aws_pinpoint_id = os.getenv('AWS_PINPOINT_APP')
aws_origination_phoneNumber = os.getenv('AWS_ORIGINATION_NUMBER')
aws_origination_email = os.getenv('AWS_ORIGINATION_EMAIL')

# check for aws configuration inside the environment
if not aws_access_key_id:
  print('AWS_ACCESS_KEY_ID is missing!')

if not aws_secret_access_key:
  print('AWS_SECRET_ACCESS_KEY is missing!')

if not aws_default_region:
  print('AWS_DEFAULT_REGION is missing!')

if not os.environ.get('AWS_SESSION_TOKEN'):
  print('AWS_SESSION_TOKEN is missing!')

if not aws_pinpoint_id:
  print(f'AWS_PINPOINT_APP is missing!')

if not aws_origination_phoneNumber:
  print(f'AWS_ORIGINATION_NUMBER')

if not aws_origination_email:
  print(f'AWS_ORIGINATION_EMAIL')

# define a restful api to connect all the resources 
api = Api(aws_pinpoint_app)

# function to generate a unique reference ID for each recipient
def generate_ref_id(destinationNumber, brandName, source):
 refId = brandName + source + destinationNumber
 return hashlib.md5(refId.encode()).hexdigest()

# a class to handle sending OTP using AWS Pinpoint
class sendOTP(Resource):
 def __init__(self, channel_id, channel, allowedAttempts, codeLength, brandName, source, language) -> None:
   super().__init__()
   self.region = aws_default_region
   self.appId = aws_pinpoint_id
   self.allowedAttempts = allowedAttempts
   self.channel = channel
   self.language = language
   self.codeLength = codeLength
   self.brandName = brandName
   self.source = source
   if channel_id == 2:
    self.channel_type = 'EMAIL'
   else:
    self.channel_type = 'SMS'

 # function that autogenerate an OTP verification code
 def generate_otp_code(self, code_length):
  """Generate a random OTP code with the specified length"""
  import random
  return ''.join([str(random.randint(0, 9)) for _ in range(code_length)])

 # send otp code to the endpoint
 def send_otp(self, validityPeriod):
  client = boto3.client('pinpoint', region_name=self.region)
  otp_code = self.generate_otp_code(code_length=self.codeLength)
  try:
   if self.channel_type == 'SMS':
    response = client.send_otp_message(
      ApplicationId = self.appId,
      SendOTPMessageRequestParameters = {
        'Channel' : 'SMS',
        'BrandName' : self.brandName,
        'CodeLength' : self.codeLength,
        'ValidityPeriod' : validityPeriod,
        'AllowedAttempts' : self.allowedAttempts,
        'Language' : self.language,
        'OriginationIdentity' : aws_origination_phoneNumber,
        'DestinationIdentity' : self.channel,
        'ReferenceId' : generate_ref_id(destinationNumber=self.channel, brandName=self.brandName, source=self.source)
      }
    )
   elif self.channel_type == 'EMAIL':
    response = client.send_message (
      ApplicationId = self.appId,
      MessageRequest={
        'Addresses' : {
          self.channel: {
            'ChannelType' : 'EMAIL'
          }
        },
        'MessageConfiguration': {
          'EmailMessage' : {
            'FromAddress' : self.source,
            'SimpleEmail' : {
              'Subject' : {
                'Charset' : 'UTF-8',
                'Data' : 'OTP Verification'
              },
              'HtmlPart' : {
                'Charset' : 'UTF-8',
                'Data' : f'<p>Your OTP verification code is: {otp_code}</p>'
              },
              'TextPart' : {
                'Charset' : 'UTF-8',
                'Data' : f'Your OTP verification code is: {otp_code}'
              }
            }
          }
        }
      }
    )
   # if the verification method is neither sms or email
   else:
    raise ValueError('Invalid channel type. Supported values: "SMS" or "EMAIL"')
   
   if response['StatusCode'] == 200:
    # render the sending otp template
    print(f'An OTP verification has been sent successfuly to {self.channel}')
    return render_template('sending_otp.html', verification_id=self.channel_type, verification_method=self.channel)

   else:
    raise ValueError
  
  except BaseException as e:
   return jsonify({'message' : f'Error sending OTP verification to {self.channel} with error: {e}'}), 400
   

 # function that verifies the OTP code
 def verify_otp(self):
  client = boto3.client('pinpoint', region_name=self.region)
  # get the user's otp from the form data
  if request.method == 'POST':
    try: 
      otp = request.form['OTP_CODE']
    except:
      return ({
        'success' : False, 
        'message' : f'Sorry! The server cannot understand the request!'
      }), 400

  try:
   response = client.verify_otp_message(
    ApplicationId = self.appId,
    VerifyOTPMessageRequestParameters = {
     'DestinationIdentity' : {
      self.channel_type.capitalize() + "Number": self.channel
     },
     'ReferenceId' : generate_ref_id(destinationNumber=self.channel, brandName=self.brandName, source=self.source),
     'Otp' : otp
    }
   )
  
  except ClientError as e:
   return jsonify({'message' : f'Error with verifying OTP verification for {self.phoneNumber} with error: {e.response}'}), 400
  else:
    print(f'Valid OTP Code')
    # grant the user the permission to view the dashboard 
    permissions = ['can_view_dashboard', 'can_register_saving_challenges', 'can_use_geolocation_api']
    for permission in permissions:
      grant_permission_to_verified_users(permission_name=permission)

    return redirect(url_for('user_dashboard'))

# connect the resource with the url using rest api
api.add_resource(sendOTP, '/studyhub/send-otp/sms/?/', '/studyhub/validate-otp/sms/?/')
