########## SIGN UP PAGE FOR USERS INPUT FOR MACHINE LEARNING ALGORITHM FOR RECOMMENDATION ENGINE #########
# import libraries
import json
from http import HTTPStatus

import jwt
from flask import Flask, Response, request
from flask_migrate import Migrate
from flask_restful import Resource, abort, fields, inputs, marshal_with, reqparse
from sqlalchemy import create_engine
from werkzeug.exceptions import Conflict

from API.locationAPI import LocationValidator
from database.users_models import UserInformation, db
from get_env import (
    database_host,
    database_name,
    database_password,
    database_port,
    database_type,
    database_username,
    secret_key,
)
from helper_functions.middleware_functions import token_required
from helper_functions.validate_users_information import validate_users_information

user_profile_app = Flask(__name__)

migrate = Migrate(user_profile_app, db)

# connect flask to postgres database using SQLALCHEMY
user_profile_app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
engine = create_engine(
    f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
)
# inspector = Inspector.from_engine(engine)

# Create the SQLAlchemy database object
db.init_app(user_profile_app)

# resources fields to serialize the response object
_user_information_resource_fields = {
    "first_name": fields.String,
    "middle_name": fields.String,
    "last_name": fields.String,
    "age": fields.Integer,
    "date_of_birth": fields.DateTime(dt_format="iso8601"),
    "address_line_1": fields.String,
    "address_line_2": fields.String,
    "city": fields.String,
    "province": fields.String,
    "country": fields.String,
    "postal_code": fields.String,
    "gender": fields.String,
    "religion": fields.String,
    "profile_image": fields.String,
    "user_bio": fields.String,
    "interests": fields.String,
    "education_institutions": fields.String,
    "education_majors": fields.String,
    "education_degrees": fields.String,
    "graduation_date": fields.DateTime(dt_format="iso8601"),
    "identification_option": fields.String,
    "identification_material": fields.String,
}


# Querying and inserting into user profile database Flask_Restful API
class UserInformationResource(Resource):
    # private methods that abort if user information exists and not exists
    def __abort_if_user_profile_exists(self, user_id) -> None:
        if user_id:
            raise Conflict
        return

    def __abort_if_user_profile_does_not_exists(self, user_id) -> None:
        if not user_id:
            raise Conflict
        return

    # private method to add argument into the form data
    def __form_data_add_arguments(self, form_data) -> None:
        form_data.add_argument(
            "first_name",
            type=str,
            help="First name is required",
            required=True,
        )
        form_data.add_argument("mid_name", type=str, required=False)
        form_data.add_argument(
            "last_name",
            type=str,
            help="Last name is required",
            required=True,
        )
        form_data.add_argument(
            "age",
            type=int,
            help="Age is required and must be larger than 18",
            required=True,
        )
        form_data.add_argument(
            "birth_day",
            type=inputs.date,
            help="Birthday is required and the format must be YYYY-MM-DD",
            required=True,
        )
        form_data.add_argument(
            "address_line_1",
            type=str,
            help="First address is required",
            required=True,
        )
        form_data.add_argument(
            "address_line_2",
            type=str,
            help="Second address is required",
            required=False,
        )
        form_data.add_argument("city", type=str, help="City is required", required=True)
        form_data.add_argument(
            "province", type=str, help="Province is required", required=True
        )
        form_data.add_argument(
            "country", type=str, help="Country is required", required=True
        )
        form_data.add_argument(
            "postal_code",
            type=str,
            help="Postal Code is required and maximum of 10 characters long",
            required=True,
        )
        form_data.add_argument(
            "gender", type=str, help="Gender is required", required=True
        )
        form_data.add_argument(
            "profile_image",
            type=str,
            help="This will be an image in bytes",
            required=False,
        )
        form_data.add_argument("religion", type=str, required=False)
        form_data.add_argument("user_bio", type=str, required=False)
        form_data.add_argument("user_interest", type=str, required=False)
        form_data.add_argument(
            "education_institutions",
            type=str,
            help="University is required",
            required=True,
        )
        form_data.add_argument(
            "education_majors",
            type=str,
            help="Majors are required",
            required=True,
        )
        form_data.add_argument(
            "education_degrees",
            type=str,
            help="Degrees are required",
            required=True,
        )
        form_data.add_argument(
            "graduation_date",
            type=inputs.date,
            help="Graduation Day is required",
            required=True,
        )
        form_data.add_argument(
            "identification_option",
            type=str,
            help="User can choose which material they want to submit in order to verify their student's status",
            required=True,
        )
        form_data.add_argument(
            "identification_material",
            type=str,
            help="User has to upload the material that verify their student's status",
            required=True,
        )

    # a private method that parse the update form data
    def __update_form_data_add_arguments(self, update_form_data):
        update_form_data.add_argument("first_name", type=str)
        update_form_data.add_argument("mid_name", type=str)
        update_form_data.add_argument("last_name", type=str)
        update_form_data.add_argument(
            "age", type=int, help="Age must be larger than 18"
        )
        update_form_data.add_argument(
            "birth_day", type=inputs.date, help="Birthday format must be YYYY-MM-DD"
        )
        update_form_data.add_argument("address_line_1", type=str)
        update_form_data.add_argument("address_line_2", type=str)
        update_form_data.add_argument("city", type=str)
        update_form_data.add_argument("province", type=str)
        update_form_data.add_argument("country", type=str)
        update_form_data.add_argument("postal_code", type=str)
        update_form_data.add_argument("gender", type=str)
        update_form_data.add_argument(
            "profile_image", type=str, help="This will be an image in bytes"
        )
        update_form_data.add_argument("religion", type=str)
        update_form_data.add_argument("user_bio", type=str)
        update_form_data.add_argument("user_interest", type=str)
        update_form_data.add_argument("education_institutions", type=str)
        update_form_data.add_argument("education_majors", type=str)
        update_form_data.add_argument("education_degrees", type=str)
        update_form_data.add_argument("graduation_date", type=inputs.date)
        update_form_data.add_argument("identification_option", type=str)
        update_form_data.add_argument(
            "identification_material",
            type=str,
            help="Identification material uploads will be convert to bytes",
        )

    # a get method to get the user profile and return to the client
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_user_information_resource_fields)  # serialize the instance object
    def get(self):
        with user_profile_app.app_context():
            # get the token from cookies
            try:
                token = request.cookies.get("token")
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_id = decoded_token["id"]  # get the user's id
                # query the database to get the user with the user id
                user = UserInformation.query.filter_by(user_id=user_id).first()
                if user:
                    return user, 200
                else:
                    raise Conflict
            except (
                Conflict
            ) as conflict_error:  # -> no user's found in the database (user has not added their profile)
                abort(404, message=f"{conflict_error}")

            except (
                Exception
            ) as error:  # -> any error being caught such as jwt token value error, signature error,...
                response_data = {
                    "message": f"{error}"  # return the error message to the client
                }
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json, status=500, mimetype="application/json"
                )
                return response

    # handle the POST request from the form data
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_user_information_resource_fields)  # serialize the response object
    def post(self):
        with user_profile_app.app_context():
            # get the token from cookies to get the user id
            user_token = request.cookies.get("token")
            # encode the token from string to bytes
            # bytes_token = bytes(user_token, 'utf-8')
            # decode the token
            decoded_user_token = jwt.decode(
                user_token, secret_key, algorithms=["HS256"]
            )
            user_id = decoded_user_token["id"]
            # get the users inputs
            try:
                # get the user's input from the form data
                form_data = reqparse.RequestParser()
                self.__form_data_add_arguments(
                    form_data
                )  # call the method to add all the arguments

                args = form_data.parse_args()
                first_name = args["first_name"]
                mid_name = args["mid_name"]
                last_name = args["last_name"]
                age = args["age"]
                birth_day = args["birth_day"]
                address_line_1 = args["address_line_1"]
                address_line_2 = args["address_line_2"]
                city = args["city"]
                province = args["province"]
                country = args["country"]
                postal_code = args["postal_code"]
                gender = args["gender"]
                religion = args["religion"]
                user_bio = args["user_bio"]
                user_interest = args["user_interest"]
                profile_image = args["profile_image"]
                education_institution = args["education_institutions"]
                education_majors = args["education_majors"]
                education_degrees = args["education_degrees"]
                graduation_date = args["graduation_date"]
                identification_option = args["identification_option"]
                identification_material = args["identification_material"]

                # Initialize the errors dictionary:
                errors = {}

                # Validate the form data, if not -> send the error messages to the front-end
                # validate the users input before insert the data into the database
                validate_users_information(
                    errors,
                    first_name,
                    last_name,
                    age,
                    birth_day,
                    gender,
                    profile_image,
                    education_institution,
                    education_majors,
                    education_degrees,
                    graduation_date,
                    identification_option,
                    identification_material,
                )

                # after getting the address, check for the validation using Google Maps Geocoding API before execute the insert the element
                # if the address is not valid
                addressChecking = LocationValidator(
                    errors,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    province=province,
                    country=country,
                    postal_code=postal_code,
                )

                # if all the fields are valid
                if not errors and addressChecking.is_valid_address():
                    # query the database to check if there is any user that already exists with the same information
                    result = UserInformation.query.filter_by(
                        user_id=user_id,
                    ).first()

                    # abort if the result is already in the database -> has to use UPDATE(PATCH) request
                    self.__abort_if_user_profile_exists(result)

                    # if the users information didn't exist in the database yet
                    # create a list of new user instance
                    new_user = UserInformation(
                        first_name=first_name,
                        middle_name=mid_name,
                        last_name=last_name,
                        age=age,
                        date_of_birth=birth_day,
                        address_line_1=address_line_1,
                        address_line_2=address_line_2,
                        city=city,
                        province=province,
                        country=country,
                        postal_code=postal_code,
                        gender=gender,
                        religion=religion,
                        profile_image=profile_image,
                        user_bio=user_bio,
                        interests=user_interest,
                        education_institutions=education_institution,
                        education_majors=education_majors,
                        education_degrees=education_degrees,
                        graduation_date=graduation_date,
                        identification_option=identification_option,
                        identification_material=identification_material,
                        user_id=user_id,
                    )

                    # add new user into users model
                    db.session.add(new_user)
                    # commit the change to the database -> 201 if successful
                    db.session.commit()

                    find_user_information = UserInformation.query.filter_by(
                        user_id=user_id
                    ).first()

                    return find_user_information, 201

                # if there is any invalid field is being caught (including address, profile image(if any)), send the error to the client with a 400 bad request status
                else:
                    raise ValueError

            # catch 400 bad request error
            except ValueError:
                db.session.rollback()
                abort(400, message=json.dumps(errors))

            # catch the 409 conflict error
            except Conflict as conflict_error:
                db.session.rollback()
                abort(409, message=f"{conflict_error}")

            # catch the error if there is an internal server error
            except Exception as e:
                db.session.rollback()
                abort(500, message=f"{e}")

    # a method to handle the UPDATE request
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_user_information_resource_fields)
    def patch(self):
        with user_profile_app.app_context():
            try:
                # get the token from cookies
                token = request.cookies.get("token")
                # decode the token
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_id = decoded_token["id"]
                # query the user_information table to see if the user id already has profile
                user_information = UserInformation.query.filter_by(
                    user_id=user_id
                ).first()

                # if no user information found
                self.__abort_if_user_profile_does_not_exists(user_information)

                # get the user's input from the form data
                update_form_data = reqparse.RequestParser()
                self.__update_form_data_add_arguments(update_form_data)

                # parse the arguments from the form data
                update_args = update_form_data.parse_args()

                # create an errors dictionary to catch the error from the form data
                errors = {}

                # check if each argument is in the update_args -> yes (update the database field), no (leave them)
                # check to see if the address is corrected
                # create 2 python dictionaries
                existing_location_data = {
                    "address_line_1": user_information.address_line_1,
                    "address_line_2": user_information.address_line_2,
                    "city": user_information.city,
                    "country": user_information.country,
                    "postal_code": user_information.postal_code,
                }

                update_location_data = {
                    "address_line_1": update_args["address_line_1"],
                    "address_line_2": update_args["address_line_2"],
                    "city": update_args["city"],
                    "province": update_args["province"],
                    "country": update_args["country"],
                    "postal_code": update_args["postal_code"],
                }

                update_location_data.update(existing_location_data)

                location_validator = LocationValidator(
                    errors,
                    **update_location_data,
                )

                # if all the fields are valid
                if not errors and location_validator.is_valid_address():
                    for args_names, args_values in update_args.items():
                        if args_values:
                            setattr(
                                user_information, args_names, args_values
                            )  # set the attributes of the arguments

                    # commit the change to the database
                    db.session.commit()

                    update_user = UserInformation.query.filter_by(
                        user_id=user_id
                    ).first()

                    # return a response to the client
                    return update_user, 201

                else:
                    raise ValueError

            except ValueError:
                db.session.rollback()
                abort(400, message=json.dumps(errors))

            # catch the 404 error
            except Conflict as conflict_error:
                db.session.rollback()
                abort(404, message=f"{conflict_error}")

            except Exception as error:
                db.session.rollback()
                abort(500, message=f"{error}")

    # a method to delete a user's profile
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_user_information_resource_fields)
    def delete(self):
        with user_profile_app.app_context():
            # get the token from cookies
            try:
                token = request.cookies.get("token")
                decoded_token = jwt.decode(
                    token, secret_key, algorithms=["HS256"]
                )  # decode the jwt token
                # get the user id
                user_id = decoded_token["id"]

                # query the database to see if the user has the profile
                find_user_profile = UserInformation.query.filter_by(
                    user_id=user_id
                ).first()

                # abort if no profile found
                self.__abort_if_user_profile_does_not_exists(find_user_profile)

                db.session.query(UserInformation).filter(
                    UserInformation.user_id == user_id
                ).delete()
                # commit the change to the database
                db.session.commit()

                # return the response to the client if there is no error occured
                response_data = {
                    "message": f"User information has been successfully deleted!"
                }
                response_json = json.dumps(response_data)
                response = Response(
                    response_json,
                    status=HTTPStatus.CREATED,
                    mimetype="application/json",
                )
                return response

            # except 404 conflict error
            except Conflict as conflict_error:
                db.session.rollback()
                abort(404, message=f"{conflict_error}")

            except (
                Exception
            ) as error:  # try to catch the error and display to the client
                db.session.rollback()
                abort(500, message=f"{error}")
