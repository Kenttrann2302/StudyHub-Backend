# test rest api for posting user profile
import datetime
import pdb
import uuid

import requests

date_str = '2003-04-01'
grad_day_str = '2027-04-30'
date = datetime.date.fromisoformat(date_str)
grad_day = datetime.date.fromisoformat(grad_day_str)

# Generate a new UUID
new_uuid = uuid.uuid4()

# Convert UUID to string
uuid_str = str(new_uuid)

BASE = "http://127.0.0.1:5000/"

# verifying otp and store the token into cookies
otp_code = int(input('Please enter the OTP code: '))

response = requests.get(BASE + '/studyhub/verify-otp/' + f'{otp_code}')
print(response.json())

# include cookies in the request headers
cookie = response.cookies.get_dict()
headers = {
 'Cookie' : f"token={cookie['token']}"
}

data = [
 {
  "firstName" : "Kent",
  "midName" : "Duy",
  "lastName" : "Tran",
  "age" : 20,
  "birthDay" : date,
  "firstAddress" : "75 Skelton Boulevard",
  "city" : "Brampton",
  "province" : "Ontario",
  "country" : "Canada",
  "postalCode" : "L6V 2S2",
  "gender" : "Male",
  "religion" : "Catholic",
  "user_bio" : "Mechatronics Engineering at University of Waterloo",
  "user_interest" : "Backend Development",
  "education_institutions" : "University of Waterloo",
  "education_majors" : "Engineering",
  "education_degrees" : "Bachelor",
  "graduation_date" : grad_day,
  "identification_option" : "Student Email Address",
  "identification_material" : "kd3tran@uwaterloo.ca"
 }
]

for i in range(len(data)):
 response = requests.post(BASE + "/studyhub/user-profile/user-information/", headers=headers, data=data[i])
 print(response.json())