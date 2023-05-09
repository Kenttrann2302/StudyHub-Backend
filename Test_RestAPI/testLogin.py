# test rest api for user's login credentials
import requests

BASE = "http://0.0.0.0:8080/"

user_login_data = [
    {
        "signIn_username": "kenttran2302",
        "signIn_password": "Khangduy230204@$",  # correct user
    },
    {
        "signIn_username": "jnfenfeife",
        "signIn_password": "eiwofmeowfneorg",  # no user found
    },
    {
        "signIn_username": "kenttran2302",
        "signIn_password": "njfgurbguegg3",  # found username but wrong password
    },
]

for i in range(len(user_login_data)):
    login_response = requests.post(
        BASE + "/studyhub/validateuser/", data=user_login_data[i]
    )
    print(login_response.json())
