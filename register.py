############### REGISTER PAGE FOR USERS TO CREATE THEIR USERNAME AND PASSWORD FOR THE APPLICATION
# import libraries
import json
import random
import time

import bcrypt
import jwt
from flask import Blueprint, Flask, Response, request, current_app
from flask_migrate import Migrate
from flask_restful import Resource, fields, marshal_with, reqparse, abort
from sqlalchemy import create_engine
from http import HTTPStatus
from werkzeug.exceptions import Conflict, NotFound, BadRequest, Forbidden, Unauthorized

# import from files
from database.users_models import Users, db
from get_env import (
    secret_key
)
from helper_functions.registerformValidation import checkpassword, checkpasswordconfirm
from helper_functions.registerformValidation import validate_registration_form
from Twilio.twilio_send_email import sendgrid_verification_email

# register the app instance with the endpoints we are using for this app
registration_routes = Blueprint("registration_routes", __name__)

# Add a test configuration
# register_app.config["TESTING"] = True
# register_app.config["WTF_CSRF_ENABLED"] = False

# global variables
# initialize all the a dictionary of validated fields for user inputs
validated_fields = {
    "username": "",
    "password": "",
    "password_confirmation": "",
    "verification_id": "",
    "verification_method": "",
}

# initialize the errors dictionary in order to store the errors for each input fields
register_errors = {}

# define a resource fields to serialize the object (user's login information) to make sure that all the identifications have been inserted success
_user_resource_fields = {
    "username": fields.String,
    "verification_method": fields.String
}

# create a resource for rest api to handle the post request
class RegistrationResource(Resource):
    # this is a method to handle the GET request from the database after inserting the user's login information into the database
    @marshal_with(_user_resource_fields)
    def get(self) -> None:
        with current_app.app_context():
            # get all the usernames and verification method from the database
            try:
                all_users = Users.query.all()
                if all_users:
                    return all_users
                else:
                    raise NotFound

            except NotFound as not_found_error:
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            except Exception as internal_server_error:
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{internal_server_error}")

    # a function generate a random 6 digits otp code
    def __generate_otp(self):
        otp = ""
        for i in range(6):
            otp += str(random.randint(0, 9))
        return otp

    # this is a function to handle the POST request from the registration form and insert the registration fields into the database
    def post(self) -> None:
        with current_app.app_context():
            try:
                # get the registration form data and validate them before inserting into the database
                registerForm = reqparse.RequestParser()
                registerForm.add_argument(
                    "username", type=str, help="Username is required", required=True
                )
                registerForm.add_argument(
                    "password", type=str, help="Password is required", required=True
                )
                registerForm.add_argument(
                    "password_confirmation",
                    type=str,
                    help="Password confirmation is required",
                    required=True,
                )
                registerForm.add_argument(
                    "verification_method",
                    type=str,
                    help="Verification method option is required",
                    required=True,
                )
                registerForm.add_argument("areacode_id", type=str, required=False)
                registerForm.add_argument(
                    "verification",
                    type=str,
                    help="Email, SMS or Device Information is required",
                    required=True,
                )

                args = registerForm.parse_args()
                username = args["username"]
                password = args["password"]
                password_confirmation = args["password_confirmation"]
                verification_method = args["verification_method"]
                areacode_id = args["areacode_id"]
                verification = args["verification"]

                new_user = [username, password, password_confirmation, verification]

                # validate the form data, if not -> send error messages to the website
                # validate the users registration input on front-end before inserting the data into the database
                validated_registration = validate_registration_form(
                    new_user=new_user,
                    errors=register_errors,
                    verification_id=verification_method,
                    areacode_id=areacode_id,
                )

                # handle appropriate validated_registration -> check if the username and password already existed
                if len(validated_registration) == 4 and not register_errors:
                    # genrate the salt for the hashed_password
                    salt = bcrypt.gensalt()
                    # hash the password using bcrypt hashing algorithm
                    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

                    decoded_hashed_password = hashed_password.decode("utf-8")

                    # query each field to make sure each of them is unique
                    username_taken = (
                        Users.query.filter(Users.username == username).first()
                        is not None
                    )

                    password_taken = (
                        Users.query.filter(
                            Users.password == decoded_hashed_password
                        ).first()
                        is not None
                    )

                    verification_method_taken = (
                        Users.query.filter(
                            Users.verification_method == verification_method,
                            Users.verification == verification,
                        ).first()
                        is not None
                    )

                    # check if there is the users input already in the database
                    if username_taken:
                        register_errors[
                            "username"
                        ] = f"Sorry! This username already exists!"
                        response_data = {
                            "message": register_errors
                        }
                        response_json = json.dumps(response_data)
                        response = Response(
                            response=response_json,
                            status=HTTPStatus.CONFLICT,
                            mimetype="application/json",
                        )
                        return response 

                    elif password_taken:
                        register_errors[
                            "password"
                        ] = f"Sorry! This password already exists!"
                        response_data = {
                            "message": register_errors
                        }
                        response_json = json.dumps(response_data)
                        response = Response(
                            response=response_json,
                            status=HTTPStatus.CONFLICT,
                            mimetype="application/json",
                        )
                        return response

                    elif verification_method_taken:
                        switch = {
                            verification_method
                            == "Email": f"Sorry! This email has been registered in our system!",
                            verification_method
                            == "Phone number": f"Sorry! This phone number has been registered in our system!",
                            verification_method
                            == "Device Push Notification": f"Sorry! This device has been registered in our system!",
                        }

                        error_message = switch.get(True, "None")
                        if error_message is not None:
                            register_errors["verification"] = error_message
                            response_data = {
                                "message": register_errors
                            }
                            response_json = json.dumps(response_data)
                            response = Response(
                                response=response_json,
                                status=HTTPStatus.CONFLICT,
                                mimetype="application/json",
                            )
                            return response

                    else: # if no field existed before
                        # create an instance to add the new user into the database
                        new_user = Users(
                            username=validated_registration[0],
                            password=decoded_hashed_password,
                            verification_method=verification_method,
                            verification=validated_registration[3],
                        )
                        # add new user to the registration model
                        db.session.add(new_user)

                        # send a confirmation email to the user to verify their account using Twillio
                        if verification_method == "Email":
                            (
                                response_status,
                                response_message,
                                temp_token,
                            ) = sendgrid_verification_email(
                                user_email=new_user.verification,
                                studyhub_code=self.__generate_otp(),
                                request_type='post'
                            )

                            # store the user's temporary token into the database
                            new_user.temp_token = temp_token
                            # commit the change to the database
                            db.session.commit()

                            # check if the response_message is True -> verification sent successfully!
                            if response_status == HTTPStatus.OK or response_status == HTTPStatus.CREATED:
                                response_data = {
                                    "message": f"Successfully!",
                                }
                                response_json = json.dumps(response_data)
                                response = Response(
                                    response=response_json,
                                    status=HTTPStatus.CREATED,
                                    mimetype="application/json",
                                )
                                return response

                            # raise and Exception error if Twilio cannot be sent
                            else:
                                raise Exception(f"{response_message}")

                        # handle the response if the verification method is not Email -> this will be done later

                else: # if there is an invalid input from the form data
                    raise BadRequest

            # catch the 400 bad request error
            except BadRequest as bad_request_error:
                db.session.rollback()
                abort(HTTPStatus.BAD_REQUEST, message=f"{bad_request_error}")

            # handle the errors if there is any errors when validating the inputs on the form
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

    # this is a function that update the user information if the user forgot their username or password
    def patch(self):
        with current_app.app_context():
            try:
                import pdb
                pdb.set_trace()
                # get the form data and parse it to get the value of the key
                update_data_form = reqparse.RequestParser()
                update_data_form.add_argument("username", type=str, help="Username is required", required=True) # get the username
                update_data_form.add_argument("new_password", type=str, help="Password is required", required=True) # get the password
                update_data_form.add_argument("new_password_confirmation", type=str, help="Password confirmation is required",required=True) # get the password confirmation
                
                # parse the form data
                update_args = update_data_form.parse_args()
                username = update_args["username"]
                password = update_args["new_password"]
                password_confirmation = update_args["new_password_confirmation"]

                # find the user in the database
                find_user_query = Users.query.filter_by(username=username).first()

                # abort if the user doesn't exist
                if not find_user_query:
                    raise NotFound
                
                # initialize a validate fields for validate the new password
                validate_new_user = []
                errors = {}
                
                # if user is found in the database
                # validate the password and password confirmation before change them in the database
                checkpassword(username=username, password=password, errors=errors, validate_new_user=validate_new_user)
                checkpasswordconfirm(confirmed_password=password_confirmation, password=password, errors=errors, validate_new_user=validate_new_user)

                # if there is no error in the errors dictionary -> handle appropriate form data
                if len(validate_new_user) == 2 and not errors:      
                    # genrate the salt for the hashed_password
                    salt = bcrypt.gensalt()
                    # hash the password using bcrypt hashing algorithm
                    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

                    decoded_hashed_password = hashed_password.decode("utf-8")

                    # query the database to check if the password is not none
                    password_taken = (
                        Users.query.filter(
                            Users.password == decoded_hashed_password
                        ).first()
                        is not None
                    )

                    # raise conflict if the password already exists in the userdatabase
                    if password_taken:
                        raise Conflict
                    
                    # if no user took this password in the database
                    # abort forbidden if the user hasn't verified their email or sms
                    if find_user_query.account_verified == False:
                        raise Forbidden

                    # send an otp to user's email to verify if the authenticated user made this change
                    if find_user_query.verification_method == "Email":
                        (
                            response_status,
                            response_message,
                            temp_token,
                        ) = sendgrid_verification_email(
                            user_email=find_user_query.verification,
                            studyhub_code=self.__generate_otp(),
                            request_type='patch', new_password=decoded_hashed_password
                        )

                        # store the user's temporary token into the database
                        find_user_query.temp_token = temp_token
                        # commit the change to the database
                        db.session.commit()

                        # check if the response_message is True -> verification sent successfully!
                        if response_status == HTTPStatus.OK or response_status == HTTPStatus.CREATED:
                            response_data = {
                                "message": f"Sending email successfully!",
                            }
                            response_json = json.dumps(response_data)
                            response = Response(
                                response=response_json,
                                status=HTTPStatus.CREATED,
                                mimetype="application/json",
                            )
                            return response

                        # raise and Exception error if Twilio cannot be sent
                        else:
                            raise Exception(f"{response_message}")
                
                else:
                    raise BadRequest
                
            # catch the not found error
            except NotFound as not_found_error:
                db.session.rollback()
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            # catch the conflict error
            except Conflict as conflict_error:
                db.session.rollback()
                abort(HTTPStatus.CONFLICT, message=f"{conflict_error}")

            # catch the forbidden error
            except Forbidden as forbidden_error:
                db.session.rollback()
                abort(HTTPStatus.FORBIDDEN, message=f"{forbidden_error}")

            # catch the bad request error
            except BadRequest as bad_request_errrors:
                db.session.rollback()
                abort(HTTPStatus.BAD_REQUEST, message=json.dumps(errors))

            # catch the server error
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")
    
    # a delete method for user to delete the account, this method 
    def delete(self):
        with current_app.app_context():
            try:
                # get the username from the form
                user_account_delete_form = reqparse.RequestParser()
                user_account_delete_form.add_argument("username", type=str, help="Username is required", required=True) # get the username

                user_account_delete_form.parse_args()
                username = user_account_delete_form["username"]

                # query the database to get the user
                find_user_query = Users.query.filter_by(username=username).first()

                # abort if user not found in the database
                if not find_user_query:
                    raise NotFound

                # if the user is found in the database
                # abort forbidden if the user hasn't verified their email or sms
                if find_user_query.account_verified == False:
                    raise Forbidden
                
                # send a verification to user's information to see if the user created this action
                if find_user_query.verification_method == "Email":
                    (
                        response_status,
                        response_message,
                        temp_token,
                    ) = sendgrid_verification_email(
                        user_email=find_user_query.verification,
                        studyhub_code=self.__generate_otp(),
                        request_type='delete', user_id=find_user_query.user_id
                    )

                    # store the user's temporary token into the database
                    find_user_query.temp_token = temp_token
                    # commit the change to the database
                    db.session.commit()

                    # check if the response_message is True -> verification sent successfully!
                    if response_status == HTTPStatus.OK or response_status == HTTPStatus.CREATED:
                        response_data = {
                            "message": f"Sending email successfully!",
                        }
                        response_json = json.dumps(response_data)
                        response = Response(
                            response=response_json,
                            status=HTTPStatus.CREATED,
                            mimetype="application/json",
                        )
                        return response

                    # raise and Exception error if Twilio cannot be sent
                    else:
                        raise Exception(f"{response_message}")

            # catch the forbidden error
            except Forbidden as forbidden_error:
                db.session.rollback()
                abort(HTTPStatus.FORBIDDEN, message=f"{forbidden_error}")
            
            # catch the not found error
            except NotFound as not_found_error:
                db.session.rollback()
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            # catch the internal server error
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")
            

# a get request to perform a query string to get the token from the url and decode to get the email address and code to verify the user's email
@registration_routes.route("/studyhub/confirm-email", methods=["GET"])
def email_verification():
    try:
        # get the token from the query string
        token = request.args.get("token")

        # decode the token
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Check if the expiration time is more than the current time
        exp_time = decoded_token["exp"]
        current_time = int(time.time())

        if exp_time > current_time:
            # check if the email address and the temporary token is correct with the record inside the database
            user_email = decoded_token["email"]

            # query the database to see if the user_email contains the correct token
            result = Users.query.filter_by(verification=user_email).first()

            if result.temp_token == token:
                # if the token is still valid
                # verified the user's email with the system
                result.account_verified = True
                result.is_active = True
                # commit the database change
                db.session.commit()

                # return the json response
                response_data = {
                    "message": f"User with email {user_email} has been successfully verified with the system!"
                }
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json, status=HTTPStatus.CREATED, mimetype="application/json"
                )
                return response

             # if the user email is invalid -> not verified
            else:
                raise Unauthorized
    
    except Unauthorized as unauthorized_error:
        db.session.rollback()
        abort(HTTPStatus.UNAUTHORIZED, message=f"{unauthorized_error}")    

    except jwt.ExpiredSignatureError as expired_token_error:
        db.session.rollback()
        abort(HTTPStatus.FORBIDDEN, message=f"{expired_token_error}")

    except Exception as server_error:
        # internal server error
        db.session.rollback()
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

# a route for user to confirm a change on their password
@registration_routes.route("/studyhub/confirm-password-change", methods=["GET"])
def confirm_password_change():
    try:
        # get the token from the query string
        token = request.args.get("token")

        # decode the token
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Check if the expiration time is more than the current time
        exp_time = decoded_token["exp"]
        current_time = int(time.time())

        if exp_time > current_time:
            # check if the email address and the temporary token is correct with the record inside the database
            user_email = decoded_token["email"]

            # query the database to see if the user_email contains the correct token
            result = Users.query.filter_by(verification=user_email).first()

            if result.temp_token == token:
                # update the user's password
                new_password = decoded_token["new_password"]
                # hashed the password and store the decoded password into the database
                result.password = new_password
                
                db.session.commit()
        
                # return the json response
                response_data = {
                    "message": f"Password updated!"
                }
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json, status=HTTPStatus.CREATED, mimetype="application/json"
                )
                return response
            
             # if the user email is invalid -> not verified
            else:
                raise Unauthorized
    
    except Unauthorized as unauthorized_error:
        db.session.rollback()
        abort(HTTPStatus.UNAUTHORIZED, message=f"{unauthorized_error}")        

    except jwt.ExpiredSignatureError as expired_token_error:
        db.session.rollback()
        abort(HTTPStatus.FORBIDDEN, message=f"{expired_token_error}")

    except Exception as server_error:
        db.session.rollback()
        # internal server error
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

# a route for user to confirm an account deletion
@registration_routes.route("/studyhub/confirm-account-deletion", methods=["GET"])
def confirm_account_deletion():
    try:
        # get the token from the query string
        token = request.args.get("token")

        # decode the token
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])

        # check if the expiration time is more than the current time
        exp_time = decoded_token["exp"]
        current_time = int(time.time())

        if exp_time > current_time:
            # check if the email address and the temporary token is correct with the record inside the database
            user_email = decoded_token["email"]
            user_id = decoded_token["user_id"]

            # query the database to see if the user_email contains the correct token
            result = Users.query.filter_by(verification=user_email).first()

            if result.temp_token == token:
                # procceed to account deletion
                db.session.query(Users).filter(
                    Users.user_id == user_id
                ).delete()
                # commit the change to the database
                db.session.commit()

                # return the json response to the client
                response_data = {
                    "message": f"Successfully deleted user!"
                }
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json, status=HTTPStatus.CREATED, mimetype="application/json"
                )
                return response
            
             # if the user email is invalid -> not verified
            else:
                raise Unauthorized

    except Unauthorized as unauthorized_error:
        db.session.rollback()
        abort(HTTPStatus.UNAUTHORIZED, message=f"{unauthorized_error}")        

    except jwt.ExpiredSignatureError as expired_token_error:
        db.session.rollback()
        abort(HTTPStatus.FORBIDDEN, message=f"{expired_token_error}")

    except Exception as server_error:
        db.session.rollback()
        # internal server error
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")