######################## RESTFUL API FOR USERS TO SIGN INTO THEIR ACCOUNT #############
import json
from datetime import datetime, timedelta

import bcrypt
import jwt
import pytz
import requests
from flask import (
    Blueprint,
    Flask,
    Response,
    make_response,
    request,
    current_app,
    redirect,
    url_for,
)
from flask_restful import Resource, fields, reqparse, abort
from http import HTTPStatus
from werkzeug.exceptions import Forbidden, BadRequest, NotFound
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

# oauth2.0 libraries
from oauthlib.oauth2 import WebApplicationClient

# import the users models from the models.py
from database.users_models import Permission, Users, UserInformation, db
from get_env import (
    aws_sending_otp,
    aws_verify_otp,
    secret_key,
    google_client_id,
    google_client_secret,
    google_discovery_url,
)
from helper_functions.grant_permission import grant_permission_to_verified_users

# register the app instance with the endpoints we are using for this app
login_routes = Blueprint("login_routes", __name__)

# User session management setup

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
    # this is a function to handle the GET request to get the token
    def get(self) -> None:
        with current_app.app_context():
            try:
                global token
                response_data = {"token": token, "user_email": user_email}
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json,
                    status=HTTPStatus.OK,
                    mimetype="application/json",
                )
                return response

            # catch the internal server errors if found
            except Exception as error:
                response_data = {"message": f"Server error: {error}"}
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json,
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                    mimetype="application/json",
                )
                return response

    # this is a function to handle the POST request from the login form data and validate them against the registration table to see if the user is already registered in the system
    def post(self) -> None:
        with current_app.app_context():
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

                # a dictionary to store the user's errors fields
                signin_errors = {}

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
                            raise Forbidden

                        # grant the permission for the user
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
                                if response.status_code == HTTPStatus.OK:
                                    # object serialize for REST API
                                    response_data = {
                                        "message": f"An OTP code to verify email has been sent successfully!",
                                        "permissions": permissions,
                                        "token": token,
                                    }

                                    response_json = json.dumps(response_data)
                                    response = Response(
                                        response=response_json,
                                        status=HTTPStatus.OK,
                                        mimetype="application/json",
                                    )

                                    return response

                                # if there is an error while sending the request to AWS Lambda function url
                                else:
                                    raise Exception

                            # Store the token in cookie local storage if the user choose sms for verification
                            response = make_response()
                            response.set_cookie(
                                "token",
                                value=token,
                                expires=datetime.now(pytz.timezone("EST"))
                                + timedelta(minutes=30),
                            )

                            # Redirect to the dashboard and some restricted resource
                            return response

                        # if cannot grant permission due to any server error
                        else:
                            raise Exception

                    # if correct username but wrong password
                    else:
                        signin_errors[
                            "signIn_password"
                        ] = f"Password is invalid! Please enter again, if you forget your password, please click on the link below to reset your password!"
                        response_data = {
                            "error": signin_errors["signIn_password"],
                        }

                        response_json = json.dumps(response_data)
                        response = Response(
                            response=response_json,
                            status=HTTPStatus.UNAUTHORIZED,
                            mimetype="application/json",
                        )
                        return response

                # User credentials are invalid
                # Return error response or redirect to login page wit error message
                else:
                    signin_errors[
                        "signIn_username"
                    ] = f"Sorry! We cannot find any user with this username and password! If you are a new user, click on the link below to register with us!"
                    response_data = {"error": signin_errors["signIn_username"]}

                    response_json = json.dumps(response_data)
                    response = Response(
                        response=response_json,
                        status=HTTPStatus.NOT_FOUND,
                        mimetype="application/json",
                    )
                    return response

            # handle forbidden error
            except Forbidden as forbidden_error:
                db.session.rollback()
                abort(HTTPStatus.FORBIDDEN, message=f"{forbidden_error}")

            # handle any internal server error
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")


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
        if response.status_code != HTTPStatus.OK:
            response_data = {"message": f"Fail to send request to AWS Client"}
            response_json = json.dumps(response_data)
            response = Response(
                response=response_json,
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                mimetype="application/json",
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
            if response.status_code == HTTPStatus.OK:
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

                # query the user information table to get the id
                find_user_profile = UserInformation.query.filter_by(
                    user_id=user.user_id
                ).first()

                # generate a new jwt token with new permissions to authenticate the user if the user has the permission to visit some certain protected resources using a middleware function
                new_token = jwt.encode(
                    {
                        "id": str(user.user_id),
                        "user_information_id": str(find_user_profile.id),
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
                )

                return token_in_cookies

            else:
                raise ValueError

        except ValueError:  # if there is an error with AWS Lambda Client
            response_dict = json.loads(response.content.decode("utf-8"))
            response_data = {"message": f"{response_dict}!"}
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
            db.session.rollback()
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"Server error: {error}")


######################### GOOGLE OAUTH 2.0 LOGIN #########################
# OAuth2.0 client setup
client = WebApplicationClient(google_client_id)


# a helper get request function to retrieve Google's provider configuration
def get_google_provider_cfg():
    try:
        return requests.get(google_discovery_url).json()
    except Exception as server_error:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")


# a flask route for login with google-oauth2.0
@login_routes.route("/studyhub/google-login/")
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Construct the request for Google login + provide scopes to retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "callback/",
        scope=["openid", "email", "profile"],  # ask google to view user's basic profile
    )
    return redirect(request_uri)


# define a flask endpoint to get the code sent from google
@login_routes.route("/studyhub/google-login/callback/")
def callback():
    # Get the authorization code from the provider
    google_authorization_code = request.args.get("code")

    # find out what URL to hit to get tokens that allow studyhub to ask for things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to google to get the token with a post request
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=google_authorization_code,
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(google_client_id, google_client_secret),
    )

    # parse the token
    client.parse_request_body_response(json.dumps(token_response.json()))

    # hit the URL from Google when it returns the user's profile information
    user_info_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(user_info_endpoint)
    user_info_response = requests.get(
        uri, headers=headers, data=body
    )  # GET request to get the response includes the user profile

    # information that google gives -> subject, email, picture, given_name (first and last name)
    # verify user's email through google
    try:
        if user_info_response.json().get("email_verified"):
            unique_id = user_info_response.json()["sub"]
            user_email = user_info_response.json()["email"]
            user_picture = user_info_response.json()["picture"]
            user_names = user_info_response.json()["given_name"]

        # if user is not verified with Google
        else:
            raise BadRequest

        # create a user instance in the database with the information provided by Google
        # see if user has been in the database
        user = Users.query.filter_by(google_id=unique_id).first()

        # if user did not exist in the database -> create user
        if not user:
            new_user = Users(
                google_id=unique_id,
                google_user_name=user_names,
                google_profile_image=user_picture,
                verification_method="Email",
                verification=user_email,
                account_verified=True,
                is_active=True,
            )

            db.session.add(new_user)
            db.session.commit()

        # log user in
        # query the database to get the new user if this is the first time user use google to sign in with studyhub
        find_user_query = Users.query.filter_by(google_id=unique_id).first()
        # give user permissions to view dashboard, use geolocation api, view and change their profile
        permission_lists = [
            "can_view_dashboard",
            "can_use_geolocation_api",
            "can_view_profile",
            "can_change_profile",
        ]
        for permission in permission_lists:
            # query the database to see if the user with this google id
            grant_permission = Permission.query.filter_by(
                user_id=find_user_query.user_id, name=permission
            ).first()
            # if the permissions are not in yet => add the permissions in
            if not grant_permission:
                grant_permission = Permission(
                    name=permission, user_id=find_user_query.user_id
                )
                db.session.add(grant_permission)

        db.session.commit()

        # query the permissions list in the user table with the user id
        permissions = [permission.name for permission in find_user_query.permissions]

        # generate a jwt token with new permissions to authenticate the user by using the  middleware function
        jwt_token = jwt.encode(
            {
                "id": str(find_user_query.user_id),
                "permissions": permissions,
                "exp": datetime.now(pytz.timezone("EST"))
                + timedelta(minutes=30),  # set the token to be expired after 30 minutes
            },
            secret_key,
            algorithm="HS256",
        )

        response_data = {"google_name": user_names, "google_picture": user_picture}

        response_json = json.dumps(response_data)
        response = Response(
            response=response_json,
            status=HTTPStatus.CREATED,
            mimetype="application/json",
        )

        # store the token into cookies
        response = make_response(response)
        response.set_cookie(
            "token",
            value=jwt_token,
            expires=datetime.now(pytz.timezone("EST")) + timedelta(minutes=30),
        )

        return response, HTTPStatus.CREATED

    except BadRequest as bad_request_message:
        abort(HTTPStatus.BAD_REQUEST, message=f"{bad_request_message}")

    except Exception as server_error:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")


################### LOGOUT ROUTE ####################
@login_routes.route("/studyhub/logout/")
def logout():
    try:
        # get the token from cookies
        token = request.cookies.get("token")

        # if token is not found -> user is not logging in
        if not token:
            raise NotFound("No token found!")

        # set the token to be expired
        response = make_response(redirect(url_for("login")))
        response.set_cookie("token", value=token, expires=0, httponly=True)

        return response

    # catch not found token error
    except NotFound as not_found_error:
        abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

    # catch the server error
    except Exception as server_error:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")
