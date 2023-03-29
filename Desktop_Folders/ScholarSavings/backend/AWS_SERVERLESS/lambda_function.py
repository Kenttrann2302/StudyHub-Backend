######### FUNCTION VERIFY OTP WITH DYNAMODB #######
import json
import boto3
import time
from flask import render_template, redirect
client = boto3.client('dynamodb')

def lambda_handler(event, context):
 # get the email address from the parameter string of the url
 email_id = event['queryStringParameters']['email_address']
 
 print("The received email id: {}".format(email_id))

 otp_from_user = event['queryStringParameters']['otp']
 print("The received otp: {}".format(otp_from_user))

 # query the table from dynamodb to verify the otp
 response = client.query(
  TableName = 'otp_holder',
  KeyConditionExpression='email_id = :email_id',
  ExpressionAttributeValues={
   ':email_id' : {'S' : email_id}
  }, ScanIndexForward = False, Limit=1)

 # if there was no OTP that was sent to the user
 if(response['Count']==0):
  return "No such OTP was sent!"

 # get the latest sent OTP code
 else:
  latest_stored_otp_value = response['Items'][0]['OTP']['N']
  print("Latest Stored OTP Value: {}".format(latest_stored_otp_value))

  # if the otp code is expired
  if(int(response['Items'][0]['EXPIRATION_TIME']['N']) < int(time.time())):
   return ({'message' : 'This OTP code is expired'}), 404
  # verify the otp from the user against the otp from the database
  else:
   if(latest_stored_otp_value==otp_from_user):
    # redirect the user to dashboard
    return redirect('http://127.0.0.1:5000/studyhub/dashboard/')
   else:
    return ({'message' : 'Invalid OTP'}), 400