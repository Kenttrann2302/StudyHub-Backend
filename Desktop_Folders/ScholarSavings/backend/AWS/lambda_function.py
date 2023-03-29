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
 # get the token from the url string
 with lambda_app.app_context():
  token = event['queryStringParameters']['token']
  
  # get the secret key from the url string
  secret_key = event['queryStringParameters']['secret_key']
  
  # decode the token and get the user's email_address
  email_id = jwt.decode(token, secret_key, algorithms=['HS256'])['verification_endpoint']

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

