# this is a helper function that using aws pinpoint service to send OTPs to user's email or SMS

# import libraries
from flask import Flask, json, jsonify
from flask_restful import Api, Resource
import hashlib
import boto3
from botocore.exceptions import ClientError
import os

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

# check for aws configuration inside the environment
if not aws_access_key_id:
  print('AWS_ACCESS_KEY_ID is missing!')

if not aws_secret_access_key:
  print('AWS_SECRET_ACCESS_KEY is missing!')

if not aws_default_region:
  print('AWS_DEFAULT_REGION is missing!')

if not os.environ.get('AWS_SESSION_TOKEN'):
  print('AWS_SESSION_TOKEN is missing!')

# define a restful api to connect all the resources 
api = Api(aws_pinpoint_app)

# function to generate a unique reference ID for each recipient
def generate_ref_id(destinationNumber, brandName, source):
 refId = brandName + source + destinationNumber
 return hashlib.md5(refId.encode()).hexdigest()

# Resource to handle sendOTP POST and GET request
class sendOTP(Resource):
 def __init__(self, region, phoneNumber, appId, allowedAttempts) -> None:
   super().__init__()
   self.region = region
   self.phoneNumber = phoneNumber
   self.appId = appId
   self.allowedAttempts = allowedAttempts

 def send_otp(self, destinationNumber, codeLength, validityPeriod, brandName, source, language):
  client = boto3.client('pinpoint', region_name=self.region)
  try:
   response = client.send_otp_message(
    ApplicationId = self.appId,
    SendOTPMessageRequestParameters = {
     'Channel' : 'SMS',
     'BrandName' : brandName,
     'CodeLength' : codeLength,
     'ValidityPeriod' : validityPeriod,
     'AllowedAttempts' : self.allowedAttempts,
     'Language' : language,
     'OriginationIdentity' : self.phoneNumber,
     'DestinationIdentity' : destinationNumber,
     'ReferenceId' : generate_ref_id(destinationNumber=destinationNumber, brandName=brandName, source=source)
    }
   )
  except ClientError as e:
   return jsonify({'message' : f'Error sending OTP verification to {self.phoneNumber} with error: {e.response}'}), 400
  else:
   return jsonify({'message' : f'Sending OTP verification to {self.phoneNumber} successfully: {response}'})


 



