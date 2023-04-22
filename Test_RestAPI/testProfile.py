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
  "first_name" : "Kent",
  "mid_name" : "Duy",
  "last_name" : "Tran",
  "age" : 20,
  "birth_day" : date,
  "first_address" : "75 Skelton Boulevard",
  "city" : "Brampton",
  "province" : "Ontario",
  "country" : "Canada",
  "postal_code" : "L6V 2S2",
  "gender" : "Male",
  "religion" : "Catholic",
  "user_bio" : "Mechatronics Engineering at University of Waterloo",
  "user_interest" : "Backend Development",
  "education_institutions" : "University of Waterloo",
  "education_majors" : "Accounting",
  "education_degrees" : "Bachelor's Degree",
  "graduation_date" : grad_day,
  "identification_option" : "Student Email Address",
  "identification_material" : "kd3tran@uwaterloo.ca"
 }
]

# test the post request which insert the data into the database
for i in range(len(data)):
 response = requests.post(BASE + "/studyhub/user-profile/user-information/", headers=headers, data=data[i])
 print(response.json())

# test the get request which query the database and get the user information
get_userProfile_response = requests.get(BASE + "/studyhub/user-profile/user-information/", headers=headers)
print(get_userProfile_response.json())

# test the patch request which update the fields in the user information
update_data = {
  "first_name" : "Kent",
  "mid_name" : "Duy",
  "last_name" : "Tran",
  "age" : 20,
  "birth_day" : date,
  "first_address" : "75 Skelton Boulevard",
  "city" : "Brampton",
  "province" : "Ontario",
  "country" : "Canada",
  "postal_code" : "L6V 2S2",
  "gender" : "Male",
  "religion" : "Catholic",
  "user_bio" : "Mechatronics Engineering at University of Waterloo",
  "user_interest" : "Backend Development",
  "education_institutions" : "University of Waterloo",
  'education_majors' : 'Chemical Engineering',
  'education_degrees' : "Master's Degree",
  "graduation_date" : grad_day,
  "identification_option" : "Student Email Address",
  "identification_material" : "kd3tran@uwaterloo.ca",
}

update_response = requests.patch(BASE + "/studyhub/user-profile/user-information/", headers=headers, data=update_data)
print(update_response.json())
