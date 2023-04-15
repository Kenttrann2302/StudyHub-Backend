# test rest api for registration form with user's log in information
import requests
import uuid

BASE = "http://127.0.0.1:5000/"

# generate a user's UUID
test_user_uuid = uuid.uuid4()

test_user_str_uuid = str(test_user_uuid)

user_data = [
 {
  'uuid' : test_user_str_uuid,
  'username' : 'kenttran2302',
  'password' : 'Duykhang230204$@',
  'password_confirmation' : 'Duykhang230204$@',
  'verification_method' : 'Email',
  'verification' : 'duykhang2302@gmail.com'
 }
]

for i in range(len(user_data)):
 registration_response = requests.post(BASE + "/studyhub/createaccount/", user_data[i])
 print(registration_response.json())

# insert the list of options for verification methods into the identification database
response = requests.get(BASE + "/studyhub/createaccount/")
print(response.json())



