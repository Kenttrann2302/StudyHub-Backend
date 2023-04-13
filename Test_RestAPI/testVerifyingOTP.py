# test the verifying OTP code rest api
import requests

BASE = 'http://127.0.0.1:5000/'

otp_code = int(input('Please enter the OTP code: '))

response = requests.get(BASE + '/studyhub/verify-otp/' + f'{otp_code}')
print(response.json())