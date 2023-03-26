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
from random import randint

# create a dynamo client
client_dynamo = boto3.resource('dynamodb')

# get the table from AWS 
table = client_dynamo.resource('otp_holder')

# define the expiration time for the OTP Code
default_ttl = 600 # 10 minutes

# an aws lambda function that send a request with an otp to the user's endpoint
def lambda_handler(event, context):
 # get the email id
 email_id = event['queryStringParameters']['email_address']

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

 return ({
  'success' : True,
  'message' : f'A verfication code was sent successfully to email:  {email_id}'
 })
