# test rest api for user profile
import requests
import uuid
import datetime

date_str = '2003-04-01'
date = datetime.date.fromisoformat(date_str)


# Generate a new UUID
new_uuid = uuid.uuid4()

# Convert UUID to string
uuid_str = str(new_uuid)

BASE = "http://127.0.0.1:5000/"


data = [
 {
  "user_id" : uuid_str, 
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
  "Gender" : 2
 }
]

response = requests.post(BASE + "/studyhub/user-profile/user-information/", data)
print(response.json())