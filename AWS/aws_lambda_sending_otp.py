# this contains 2 AWS Lambda functions that send the otp verification that is generated in AWS DynamoDB and verify the user's otp with the otp from the db that was sent to the user's email

'''
DynamoDB Table:
--------------
Table Name: otp_holder
Primary Key: email_id
Sort Key: EXPIRATION_TIME
'''

'''
GENERATE OTP:
-------------
'''
# import libraries
import json
import boto3
import time 
import jwt
import os
from flask import Flask, request, render_template
from random import randint

lambda_app = Flask(__name__)

# create a dynamo client
client_dynamo = boto3.resource('dynamodb')

# get the table from AWS 
table = client_dynamo.Table('otp_holder')

# define the expiration time for the OTP Code
default_ttl = 600 # 10 minutes

# an aws lambda function that send a request with an otp to the user's endpoint
def lambda_handler(event, context):
 with lambda_app.app_context():
  # get the jwt token that has been stored in the http request header
  token = None
  # get the secret key decoding the jwt token from the environment variable
  secret_key = os.environ.get('secret_key')
  
  # Check if Authorization header is present in the event
  if 'headers' in event and 'Authorization' in event['headers']:
   auth_header = event['headers']['Authorization']
   # Check if Authorization header has Bearer scheme
   if auth_header.startswith('Bearer '):
    # Extract the token value
    token = auth_header.split(' ')[1]
    
  # decode the secret key that is stored in AWS Environment
  
    
  # decode the token to get the user's email address
  decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
  email_id = decoded_token['verification_endpoint']
 
  # generate a 6 digits otp code
  otp_value = randint(100000, 999999)
 
  # create an entry to send a request
  entry = {
   'email_id' : email_id,
   'OTP' : otp_value,
   'EXPIRATION_TIME' : int(time.time()) + default_ttl
  }
 
  # put the item into the table
  response=table.put_item(Item=entry)
  
  # Render the template with the form for the users to enter the OTP that was sent to their email address
  return {
      "statusCode": 200,
      "headers": {"Content-Type": "text/html"},
      "body": render_template("sending_otp.html", email_address=email_id)
  }


