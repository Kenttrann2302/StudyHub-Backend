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

################# FUNCTION HANDLER SENDING THE OTP TO THE EMAIL ADDRESS ############
import json
import boto3

client = boto3.client("ses")

def lambda_handler(event, context):
 print(event)
 if(event['Records'][0]['eventName'] == 'INSERT'):
  mail_id = event['Records'][0]['dynamodb']['Keys']['email_id']['S']
  print("The mail id is: {}".format(mail_id))

  otp=event['Records'][0]['dynamodb']['NewImage']['OTP']['N']
  print("The mail id is {}".format(otp))

  body = """
         Please use this 6 digits OTP code to verify your login at StudyHub<br>

         {}
  """.format(otp)

  message = {"Subject" : {"Data":'Your OTP verification code will be valid for only 10 minutes!'}, "Body" : {"HTML" : {"Data" : body}}}

  response = client.send_email(Source = 'duykhang2302@gmail.com',  Destination = {"ToAddresses" : [mail_id]}, Message=message)

  print(f"The email has been sent successfully!")
 


######### FUNCTION VERIFY OTP WITH DYNAMODB #######
import json
import boto3
import time
client = boto3.client('dynamodb')

def lambda_handler(event, context):
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
    return ({'message' : 'You are verified!'}), 200
   else:
    return ({'message' : 'Invalid OTP'}), 400