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
 

