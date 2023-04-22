######################## RESTFUL API FOR USERS TO SIGN INTO THEIR ACCOUNT #############
import json
from datetime import datetime, timedelta

import bcrypt
import jwt
import pytz
import requests
from flask import Blueprint, Flask, Response, make_response, request
from flask_restful import Resource, fields, reqparse
from sqlalchemy import create_engine

# import the users models from the models.py
from database.users_models import Permission, Users, db
from get_env import (
    aws_sending_otp,
    aws_verify_otp,
    database_host,
    database_name,
    database_password,
    database_port,
    database_type,
    database_username,
    secret_key,
)
from helper_functions.grant_permission import grant_permission_to_verified_users
from helper_functions.validate_users_information import create_validated_fields_dict

# login app configuration
login_app = Flask(__name__)
# login_app.config['SERVER_NAME'] = '127.0.0.1:5000'
# login_app.config['APPLICATION_ROOT'] = '/'
# login_app.config['PREFERRED_URL_SCHEME'] = 'http'
# login_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# login_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(login_app)

# register the app instance with the endpoints we are using for this app
login_routes = Blueprint("login_routes", __name__)

# Add an API Test Configuration
login_app.config["TESTING"] = True
login_app.config["WTF_CSRF_ENABLED"] = False

# connect to the userdatabase where storing all the username, password, email and phone number
login_app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
engine = create_engine(
    f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
)

# global variables
# initialize an errors dictionary to notify the error message on the front-end for the user
signin_errors = {}

# initialize all the a dictionary of validated fields for user inputs
validated_fields = {"username": "", "password": ""}

# define a resource field to serialize the response when perform a POST request to validate the user's credentials
user_resource_fields = {
    "message": fields.String,
    "user_id": fields.String,
    "username": fields.String,
    "verification_method": fields.String,
    "verification": fields.String,
    "permissions": fields.List(fields.String),
}

# create a resource for REST API to handle the POST request that handle the form data when the user sign in with their username and pass
# global the token and user's email so the token and email from the POST request can also be used to handle the GET request
token = None
user_email = None


class SignInResource(Resource):
    def __init__(self) -> None:
        super().__init__()

    # this is a function to handle the GET request to get the token
    def get(self) -> None:
        with login_app.app_context():
            if request.method == "GET":
                try:
                    global token
                    response_data = {"token": token, "user_email": user_email}
                    response_json = json.dumps(response_data)
                    response = Response(
                        response=response_json, status=200, mimetype="application/json"
                    )
                    return response

                # catch the errors if found
                except Exception as error:
                    response_data = {
                        "message": f"There is an error occured while handling the GET request to server: {error}"
                    }
                    response_json = json.dumps(response_data)
                    response = Response(
                        response=response_json, status=500, mimetype="application/json"
                    )
                    return response

    # this is a function to handle the POST request from the login form data and validate them against the registration table to see if the user is already registered in the system
    def post(self) -> None:
        with login_app.app_context():
            if request.method == "POST":
                try:
                    # get the form data include username and password and validate them against the database
                    signInForm = reqparse.RequestParser()
                    signInForm.add_argument(
                        "signIn_username",
                        type=str,
                        help="Username is required for logging in",
                        required=True,
                    )
                    signInForm.add_argument(
                        "signIn_password",
                        type=str,
                        help="Password is required for logging in",
                        required=True,
                    )

                    args = signInForm.parse_args()
                    signIn_username = args["signIn_username"]
                    signIn_password = args["signIn_password"]

                    # Get the fields that are validated
                    create_validated_fields_dict(
                        validated_fields=validated_fields,
                        username=signIn_username,
                        password=signIn_password,
                    )

                    # Query user record from database
                    user = Users.query.filter(Users.username == signIn_username).first()

                    # Validate user credentials
                    if user:
                        # if the username and password is correct
                        if bcrypt.checkpw(
                            signIn_password.encode("utf-8"),
                            user.password.encode("utf-8"),
                        ):
                            # User credentials are valid
                            # verified if the user's verification method has been verified with StudyHub system
                            if user.account_verified == False:
                                # abort if the user did not verify their email or sms or device push notification
                                response_data = {
                                    "message": f"Sorry! But it seems like you need to verify your {user.verification_method} with our system!"
                                }
                                response_json = json.dumps(response_data)
                                response = Response(
                                    response_json,
                                    status=403,
                                    mimetype="application/json",
                                )
                                return response

                            # grant permissions for the users to view the dashboard, use geolocation, view, upload and update their own profile
                            # give the user the permission to view, upload or update their profile
                            #  permissions_list = ['can_view_dashboard', 'can_view_profile', 'can_upload_profile', 'can_update_profile', 'can_use_geolocation_api']
                            permissions_list = ["can_verify_otp"]
                            for permission in permissions_list:
                                grant_permission_response = (
                                    grant_permission_to_verified_users(
                                        permission_name=permission,
                                        db=db,
                                        Users=Users,
                                        Permission=Permission,
                                    )
                                )

                            # if grant permission return successfully
                            if grant_permission_response:
                                # Generate JWT token and store it in cookies
                                # query the permissions list in the user table with the user id
                                permissions = [
                                    permission.name for permission in user.permissions
                                ]
                                global token
                                global user_email
                                user_email = user.verification
                                token = jwt.encode(
                                    {
                                        "id": str(user.user_id),
                                        "username": user.username,
                                        "verification_id": user.verification_method,
                                        "verification_endpoint": user.verification,
                                        "exp": datetime.now(pytz.timezone("EST"))
                                        + timedelta(minutes=10),
                                        "permissions": permissions,
                                    },
                                    secret_key,
                                    algorithm="HS256",
                                )

                                # if the user's verification option is an email address, then redirect the user to the enpoint of lambda functions to send OTP Verification code
                                if user.verification_method == "Email":
                                    # store the token into the request header and send it to aws lambda function
                                    headers = {"Authorization": f"Bearer {token}"}

                                    response = requests.get(
                                        url=aws_sending_otp, headers=headers
                                    )

                                    # if the GET request towards AWS API Gateway successfully
                                    if response.status_code == 200:
                                        # save to verify token to the database along with the user_id
                                        user.verify_otp_token = token

                                        # object serialize for REST API
                                        response_data = {
                                            "message": f"An OTP code to verify {user.user_id} with email: {user.verification} has been sent successfully!",
                                            "user_id": str(user.user_id),
                                            "username": user.username,
                                            "verification_method": user.verification_method,
                                            "verification": user.verification,
                                            "permissions": permissions,
                                            "token": token,
                                        }

                                        response_json = json.dumps(response_data)
                                        response = Response(
                                            response=response_json,
                                            status=200,
                                            mimetype="application/json",
                                        )

                                        return response

                                    # if there is an error while sending the request to AWS Lambda function url
                                    else:
                                        response_data = {
                                            "message": f"Sending an OTP code to the user's email resulted in errors with status code: {response.status_code}"
                                        }

                                        response_json = json.dumps(response_data)
                                        response = Response(
                                            response=response_json,
                                            status=response.status_code,
                                            mimetype="application/json",
                                        )

                                        return response

                                # Store the token in cookie local storage if the user choose sms for verification
                                response = make_response()
                                response.set_cookie(
                                    "token",
                                    value=token,
                                    expires=datetime.now(pytz.timezone("EST"))
                                    + timedelta(minutes=30),
                                    httponly=True,
                                )

                                # Redirect to the dashboard and some restricted resource
                                return response

                            # if cannot grant permission due to any server error
                            else:
                                response_data = {
                                    "message": f"There is an internal server error while granting the permission for the user!"
                                }
                                response_json = json.dumps(response_data)
                                response = Response(
                                    response=response_json,
                                    status=500,
                                    mimetype="application/json",
                                )
                                return response

                        # if correct username but wrong password
                        else:
                            signin_errors[
                                "signIn_password"
                            ] = f"Password is invalid! Please enter again, if you forget your password, please click on the link below to reset your password!"
                            response_data = {
                                "error": signin_errors["signIn_password"],
                                "validated_fields": validated_fields,
                            }

                            response_json = json.dumps(response_data)
                            response = Response(
                                response=response_json,
                                status=401,
                                mimetype="application/json",
                            )
                            return response

                    # User credentials are invalid
                    # Return error response or redirect to login page wit error message
                    else:
                        signin_errors[
                            "signIn_username"
                        ] = f"Sorry! We cannot find any user with this username and password! If you are a new user, click on the link below to register with us!"
                        response_data = {
                            "error": signin_errors["signIn_username"],
                            "validated_fields": validated_fields,
                        }

                        response_json = json.dumps(response_data)
                        response = Response(
                            response=response_json,
                            status=404,
                            mimetype="application/json",
                        )
                        return response

                # handle any internal server error
                except Exception as error:
                    response_data = {
                        "message": f"Sorry! The server cannot process the request due to an internal server error: {error}"
                    }
                    response_json = json.dumps(response_data)
                    response = Response(
                        response=response_json, status=500, mimetype="application/json"
                    )
                    return response


# create a resource for the Rest API to handle the GET request to the AWS Verify OTP Lambda function to verify the user's otp code
class verifyOTP(Resource):
    def __init__(self) -> None:
        super().__init__()

    # a GET request along with the OTP code and the token
    def get(self, otp_code):
        # get request to get the token from the aws sending otp lambda function
        get_token_url = "http://127.0.0.1:5000/studyhub/validateuser/"

        response = requests.get(get_token_url)

        # if response is unsuccessful
        if response.status_code != 200:
            response_data = {
                "message": f"Failed to get the token from the url with status code: {response.status_code}"
            }
            response_json = json.dumps(response_data)
            response = Response(
                response=response_json, status=500, mimetype="application/json"
            )
            return response

        try:
            # get the token
            response_content = response.content
            response_dict = json.loads(response_content)
            user_token = response_dict["token"]
            user_email = response_dict["user_email"]

            # query the database to get the user with the user's email
            user = Users.query.filter_by(verification=user_email).first()

            # perform a GET request to the AWS Lambda function with the token and the otp_code
            headers = {"Authorization": f"Bearer {user_token}"}
            response = requests.get(aws_verify_otp + f"{otp_code}", headers=headers)

            # if the request was made successfully
            if response.status_code == 200:
                # give the users permission to view the dashboard, use geolocation api, view and change their profile for the algorithms
                permission_lists = [
                    "can_view_dashboard",
                    "can_use_geolocation_api",
                    "can_view_profile",
                    "can_change_profile",
                ]
                for permission in permission_lists:
                    # query the database to see if the user with this email id already has these permissions
                    grant_permission = Permission.query.filter_by(
                        user_id=user.user_id, name=permission
                    ).first()
                    # if they are not in then add the permissions in
                    if not grant_permission:
                        grant_permission = Permission(
                            name=permission, user_id=user.user_id
                        )
                        db.session.add(grant_permission)

                db.session.commit()

                # query the permissions list in the user table with the user id
                permissions = [permission.name for permission in user.permissions]

                # generate a new jwt token with new permissions to authenticate the user if the user has the permission to visit some certain protected resources using a middleware function
                new_token = jwt.encode(
                    {
                        "id": str(user.user_id),
                        "username": user.username,
                        "verification_id": user.verification_method,
                        "verification_endpoint": user.verification,
                        "permissions": permissions,
                        "exp": datetime.now(pytz.timezone("EST"))
                        + timedelta(
                            minutes=30
                        ),  # set the token to be expired after 30 minutes
                    },
                    secret_key,
                    algorithm="HS256",
                )

                response_dict = json.loads(response.content.decode("utf-8"))
                response_data = {"aws_message": response_dict}

                response_json = json.dumps(response_data)
                # response = Response(response_json, status=200, mimetype='application/json')

                # store the token into cookies
                token_in_cookies = make_response(response_json)
                token_in_cookies.set_cookie(
                    "token",
                    value=new_token,
                    expires=datetime.now(pytz.timezone("EST")) + timedelta(minutes=30),
                    httponly=True,
                )

                return token_in_cookies

            else:
                raise ValueError

        except ValueError:  # if there is an error with AWS Lambda Client
            response_dict = json.loads(response.content.decode("utf-8"))
            response_data = {
                "message": f"Failed to verify user with user email: {user_email} : {response_dict}!"
            }
            response_json = json.dumps(response_data)
            response = Response(
                response=response_json,
                status=response.status_code,
                mimetype="application/json",
            )
            return response

        except (
            Exception
        ) as error:  # if the server catches the server-side error during handling the request
            response_data = {
                "message": f"There is an internal server error while verifying user otp: {error}"
            }
            response_json = json.dumps(response_data)
            response = Response(
                response=response_json, status=500, mimetype="application/json"
            )
            return response


# add login_routes to write the unit test the rest api
