# test rest api for posting user profile
import datetime
import uuid

import requests


################################# USER PROFILE #################################

################################# USER INFORMATION #################################
date_str = "2003-04-01"
grad_day_str = "2027-04-30"
date = datetime.date.fromisoformat(date_str)
grad_day = datetime.date.fromisoformat(grad_day_str)

# Generate a new UUID
new_uuid = uuid.uuid4()

# Convert UUID to string
uuid_str = str(new_uuid)

BASE = "http://0.0.0.0:8080/"

# verifying otp and store the token into cookies
otp_code = int(input("Please enter the OTP code: "))

response = requests.get(BASE + "/studyhub/verify-otp/" + f"{otp_code}")
print(response.json())

# include cookies in the request headers
cookie = response.cookies.get_dict()
headers = {"Cookie": f"token={cookie['token']}"}

# POST REQUEST
data = [
    {
        "first_name": "Kent",
        "mid_name": "Duy",
        "last_name": "Tran",
        "age": 20,
        "birth_day": date,
        "address_line_1": "75 Skelton Boulevard",
        "city": "Brampton",
        "province": "Ontario",
        "country": "Canada",
        "postal_code": "L6V 2S2",
        "gender": "Male",
        "religion": "Catholic",
        "user_bio": "Mechatronics Engineering at University of Waterloo",
        "user_interest": "Backend Development",
        "education_institutions": "University of Waterloo",
        "education_majors": "Accounting",
        "education_degrees": "Bachelor's Degree",
        "graduation_date": grad_day,
        "identification_option": "Student Email Address",
        "identification_material": "kd3tran@uwaterloo.ca",
    }
]

print("\n")
print("-" * 10)
print("USER INFORMATION MANUAL TEST")
print("\n\n")

# test the post request which insert the data into the database
for i in range(len(data)):
    post_user_information_response = requests.post(
        BASE + "/studyhub/user-profile/user-information/", headers=headers, data=data[i]
    )
    print("Post data:")
    print(post_user_information_response.json())

# get the new token from cookies
new_cookie = post_user_information_response.cookies.get_dict()
new_headers = {"Cookie": f"token={new_cookie['token']}"}

print("\n\n")

# GET REQUEST
# test the get request which query the database and get the user information
get_userProfile_response = requests.get(
    BASE + "/studyhub/user-profile/user-information/", headers=new_headers
)
print("Get data:")
print(get_userProfile_response.json())


print("\n\n")
# UPDATE REQUEST
# test the patch request which update the fields in the user information
update_data = {
    "education_majors": "Chemical Engineering",
    "education_degrees": "Master's Degree",
}

update_response = requests.patch(
    BASE + "/studyhub/user-profile/user-information/",
    headers=new_headers,
    data=update_data,
)
print("Update data:")
print(update_response.json())


################################# STUDY PREFERENCES #################################
# POST REQUEST
print("\n\n\n")
print("-" * 10)
print("STUDY PREFERENCES MANUAL TEST")
print("\n\n")
print("Post data: ")
post_user_study_preferences = [
    # all fields are included and correct -> 201 response
    {
        "study_env_preferences": "Quiet study areas",
        "study_time_preferences": "Early morning (5am-8am)",
        "time_management_preferences": "Pomodoro technique",
        "study_techniques_preferences": "The Feynman Technique",
        "courses_preferences": "MATH115, MTE121, MTE140",
        "communication_preferences": "Facebook",
    }
]

for i in range(len(post_user_study_preferences)):
    post_study_pref_response = requests.post(
        BASE + "/studyhub/user-profile/study-preferences/",
        headers=new_headers,
        data=post_user_study_preferences[i],
    )
    print(post_study_pref_response.json())

print("\n\n")
# GET REQUEST
print("Get data: ")
get_study_pref_response = requests.get(
    BASE + "/studyhub/user-profile/study-preferences/", headers=new_headers
)
print(get_study_pref_response.json())

update_user_study_preferences = [
    # all update fields are correct
    {"communication_preferences": "Twitter", "study_env_preferences": "Outdoors"}
]

print("\n\n")
print("Update data:")
# PATCH REQUEST
for i in range(len(update_user_study_preferences)):
    patch_study_pref_response = requests.patch(
        BASE + "/studyhub/user-profile/study-preferences/",
        headers=new_headers,
        data=update_user_study_preferences[i],
    )
    print(patch_study_pref_response.json())
