# test rest api for registration form with user's log in information
import uuid

import requests

BASE = "https://127.0.0.1:5000/"

# generate a user's UUID
test_user_uuid = uuid.uuid4()
test_user_str_uuid = str(test_user_uuid)

################################# TEST POST REQUEST TO CREATE AN ACCOUNT FOR USER ###########################
post_user_data = [
    {
        "uuid": test_user_str_uuid,
        "username": "kenttran2302",
        "password": "Duykhang230204$@",
        "password_confirmation": "Duykhang230204$@",
        "verification_method": "Email",
        "verification": "duykhang2302@gmail.com",
    }
]

print("\n\n\n")
print("-" * 10)
print("REGISTRATION MANUAL TEST")
print("\n\n")
print("Post data: ")
for i in range(len(post_user_data)):
    registration_response = requests.post(
        BASE + "/studyhub/user-account/", post_user_data[i]
    )
    print(registration_response.json())


################################# TEST GET REQUEST TO GET THE ACCOUNT INFORMATION OF USER ######################
print("\n\n")
# GET REQUEST
print("Get data: ")
# insert the list of options for verification methods into the identification database
response = requests.get(BASE + "/studyhub/user-account/")
print(response.json())


################################# TEST PATCH REQUEST TO UPDATE ACCOUNT INFORMATION ##########################
print("\n\n")
print("Update data:")
patch_user_data = [
    # all fields are correct
    {
        "username": "kenttran2302",
        "new_password": "Khangduy230204@$",
        "new_password_confirmation": "Khangduy230204@$",
    }
]

for i in range(len(patch_user_data)):
    update_response = requests.patch(
        BASE + "/studyhub/user-account/", patch_user_data[i]
    )
    print(update_response.json())
