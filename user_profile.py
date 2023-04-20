########## SIGN UP PAGE FOR USERS INPUT FOR MACHINE LEARNING ALGORITHM FOR SAVING STRATEGIES #########
# import libraries
import json
import os
import pdb
from datetime import datetime
from http import HTTPStatus

import jwt
from flask import Flask, Response, abort, jsonify, request
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Resource, inputs, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

# import other files
from API.locationAPI import checkAddress
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
from helper_functions.validate_users_information import (
    create_validated_fields_dict,
    validate_users_information,
)

user_profile_app = Flask(__name__)
# user_profile_app.config['SERVER_NAME'] = '127.0.0.1:5000'
# user_profile_app.config['APPLICATION_ROOT'] = '/'
# user_profile_app.config['PREFERRED_URL_SCHEME'] = 'http'
# user_profile_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

migrate = Migrate(user_profile_app, db)

# change the size for accepting files in the requests
user_profile_app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 megabytes

# connect flask to postgres database using SQLALCHEMY
user_profile_app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
engine = create_engine(
    f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
)
inspector = Inspector.from_engine(engine)

# Create the SQLAlchemy database object
db.init_app(user_profile_app)

# global resources fields to serialize the response object
userInformation_resource_fields = {
    'first_name' : fields.String,
    'middle_name' : fields.String,
    'last_name' : fields.String,
    'age' : fields.Integer,
    'date_of_birth' : fields.DateTime(dt_format='iso8601'),
    'address_line_1' : fields.String,
    'address_line_2' : fields.String,
    'city' : fields.String,
    'province' : fields.String,
    'country' : fields.String,
    'postal_code' : fields.String,
    'gender' : fields.String,
    'religion' : fields.String,
    'profile_image' : fields.String,
    'user_bio' : fields.String,
    'interests' : fields.String,
    'education_institutions' : fields.String,
    'education_majors' : fields.String,
    'education_degrees' : fields.String,
    'graduation_date' : fields.DateTime(dt_format='iso8601'),
    'identification_option' : fields.String,
    'identification_material' : fields.String,
    'user_id' : fields.String
}





# Querying and inserting into user profile database Flask_Restful API
class UserInformationResource(Resource):
    def __init__(self) -> None:
        super().__init__()

    # private method to add argument into the form data
    def __formData_addArguments(self, formData) -> None:
        formData.add_argument(
            "firstName",
            type=str,
            help="First name is required",
            required=True,
        )
        formData.add_argument("midName", type=str, required=False)
        formData.add_argument(
            "lastName",
            type=str,
            help="Last name is required",
            required=True,
        )
        formData.add_argument(
            "age",
            type=int,
            help="Age is required and must be larger than 18",
            required=True,
        )
        formData.add_argument(
            "birthDay",
            type=inputs.date,
            help="Birthday is required and the format must be YYYY-MM-DD",
            required=True,
        )
        formData.add_argument(
            "firstAddress",
            type=str,
            help="First address is required",
            required=True,
        )
        formData.add_argument(
            "secondAddress",
            type=str,
            help="Second address is required",
            required=False,
        )
        formData.add_argument(
            "city", type=str, help="City is required", required=True
        )
        formData.add_argument(
            "province", type=str, help="Province is required", required=True
        )
        formData.add_argument(
            "country", type=str, help="Country is required", required=True
        )
        formData.add_argument(
            "postalCode",
            type=str,
            help="Postal Code is required and maximum of 10 characters long",
            required=True,
        )
        formData.add_argument(
            "gender", type=str, help="Gender is required", required=True
        )
        formData.add_argument(
            "profile_image",
            type=str,
            help="This will be an image in bytes",
            required=False,
        )
        formData.add_argument("religion", type=str, required=False)
        formData.add_argument("user_bio", type=str, required=False)
        formData.add_argument("user_interest", type=str, required=False)
        formData.add_argument(
            "education_institutions",
            type=str,
            help="University is required",
            required=True,
        )
        formData.add_argument(
            "education_majors",
            type=str,
            help="Majors are required",
            required=True,
        )
        formData.add_argument(
            "education_degrees",
            type=str,
            help="Degrees are required",
            required=True,
        )
        formData.add_argument(
            "graduation_date",
            type=inputs.date,
            help="Graduation Day is required",
            required=True,
        )
        formData.add_argument(
            "identification_option",
            type=str,
            help="User can choose which material they want to submit in order to verify their student's status",
            required=True,
        )
        formData.add_argument(
            "identification_material",
            type=str,
            help="User has to upload the material that verify their student's status",
            required=True,
        )

    # a private method that is responsible for update the form data
    # def __update_formData_addArguments(self, formData):
    #     formData.add_argument(
    #         "firstName",
    #         type=str
    #     )
    #     formData.add_argument("midName", type=str)
    #     formData.add_argument(
    #         "lastName",
    #         type=str
    #     )
    #     formData.add_argument(
    #         "age",
    #         type=int,
    #         help="Age must be larger than 18"
    #     )
    #     formData.add_argument(
    #         "birthDay",
    #         type=inputs.date,
    #         help="Birthday's format must be YYYY-MM-DD"
    #     )
    #     formData.add_argument(
    #         "firstAddress",
    #         type=str,
    #     )
    #     formData.add_argument(
    #         "secondAddress",
    #         type=str
    #     )
    #     formData.add_argument(
    #         "city", type=str
    #     )
    #     formData.add_argument(
    #         "province", type=str
    #     )
    #     formData.add_argument(
    #         "country", type=str
    #     )
    #     formData.add_argument(
    #         "postalCode",
    #         type=str
    #     )
    #     formData.add_argument(
    #         "gender", type=str
    #     )
    #     formData.add_argument(
    #         "profile_image",
    #         type=str
    #     )
    #     formData.add_argument("religion", type=str)
    #     formData.add_argument("user_bio", type=str)
    #     formData.add_argument("user_interest", type=str)
    #     formData.add_argument(
    #         "education_institutions",
    #         type=str
    #     )
    #     formData.add_argument(
    #         "education_majors",
    #         type=str
    #     )
    #     formData.add_argument(
    #         "education_degrees",
    #         type=str
    #     )
    #     formData.add_argument(
    #         "graduation_date",
    #         type=inputs.date
    #     )
    #     formData.add_argument(
    #         "identification_option",
    #         type=str,
    #         help='User has to choose one of the identification options available!'
    #     )
    #     formData.add_argument(
    #         "identification_material",
    #         type=str,
    #         help="User has to upload the identification material that fits their chosen option and their student's status"
    #     )

    # a get method to get the user profile and return to the client
    @token_required(permission_list=[
        "can_view_dashboard",
        "can_view_profile",
        "can_change_profile"
    ], secret_key=secret_key)
    @marshal_with(userInformation_resource_fields)  # serialize the instance object
    def get(self):
        with user_profile_app.app_context():
            if request.method == 'GET':
                # get the token from cookies
                try:
                    token = request.cookies.get("token")
                    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
                    user_id = decoded_token['id']  # get the user's id
                    # query the database to get the user with the user id
                    user = UserInformation.query.filter_by(user_id=user_id).first()
                    if user:
                        return user
                    else:
                        raise ValueError
                except ValueError: # -> no user's found in the database (user has not added their profile)
                    response_data = ({
                        'message' : f"No user found!"
                    })
                    response_json = json.dumps(response_data)
                    response = Response(response=response_json, status=HTTPStatus.CREATED, mimetype='application/json')
                    return response
                except Exception as error: # -> any error being caught such as jwt token value error, signature error,...
                    response_data = ({
                        'message': f"Error while getting the user's information from the database: {error}"
                    })
                    response_json = json.dumps(response_data)
                    response = Response(response=response_json, status=HTTPStatus.CREATED, mimetype='application/json')
                    return response

    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    # handle the POST request from the form data from user_profile.html
    def post(self):
        with user_profile_app.app_context():
            # get the request method
            if request.method == "POST":
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
                    formData = reqparse.RequestParser()
                    self.__formData_addArguments(formData) # call the method to add all the arguments

                    args = formData.parse_args()
                    firstName = args["firstName"]
                    midName = args["midName"]
                    lastName = args["lastName"]
                    age = args["age"]
                    birthDay = args["birthDay"]
                    firstAddress = args["firstAddress"]
                    secondAddress = args["secondAddress"]
                    city = args["city"]
                    province = args["province"]
                    country = args["country"]
                    postalCode = args["postalCode"]
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
                        firstName,
                        lastName,
                        age,
                        birthDay,
                        gender,
                        profile_image,
                        education_institution,
                        education_majors,
                        education_degrees,
                        graduation_date,
                        identification_option,
                        identification_material,
                    )

                    # create a dictionary to store the validated fields by calling the helper function
                    # create_validated_fields_dict(
                    #     validated_fields=validated_fields,
                    #     firstName=firstName,
                    #     midName=midName,
                    #     lastName=lastName,
                    #     age=age,
                    #     birthDay=birthDay,
                    #     firstAddress=firstAddress,
                    #     secondAddress=secondAddress,
                    #     city=city,
                    #     province=province,
                    #     country=country,
                    #     postalCode=postalCode,
                    #     gender=gender,
                    #     religion=religion,
                    #     user_bio=user_bio,
                    #     user_interest=user_interest,
                    # )

                    # after getting the address, check for the validation using Google Maps Geocoding API before execute the insert the element
                    # if the address is not valid
                    addressChecking = checkAddress(
                        errors,
                        firstAddress,
                        city,
                        province,
                        country,
                        postalCode,
                        secondAddress,
                    )

                    # if all the fields are valid
                    if not errors and addressChecking.is_valid_address():
                        # query the database to check if there is any user that already exists with the same information
                        result = UserInformation.query.filter_by(
                            first_name=firstName,
                            middle_name=midName,
                            last_name=lastName,
                            age=age,
                            date_of_birth=birthDay,
                            address_line_1=firstAddress,
                            address_line_2=secondAddress,
                            city=city,
                            province=province,
                            country=country,
                            postal_code=postalCode,
                            gender=gender,
                            religion=religion,
                            profile_image=profile_image,
                            education_institutions=education_institution,
                            education_majors=education_majors,
                            education_degrees=education_degrees,
                            graduation_date=graduation_date,
                            identification_option=identification_option,
                            identification_material=identification_material,
                            user_id=user_id,
                        ).first()

                        # abort if the result is already in the database -> has to use UPDATE(PATCH) request
                        if result:
                            abort(
                                403,
                                {
                                    'message' : f"This user with {user_id} already existed in the database!"
                                }
                            )  # user's profile already exists in the database

                        # check if user info already exists in the database then update the user's information based on the user id from the token
                        # if result: # use update or patch request
                        #   # try update the user's information in the database
                        #   try:
                        #     print(f'Found user {user_id} in the database! Now update the users information.')
                        #     # create a list of columns need to be update
                        #     columns = [result.first_name, result.middle_name, result.last_name, result.age, result.date_of_birth, result.address_line_1, result.address_line_2, result.city, result.province, result.country, result.postal_code, result.gender_id, result.religion, result.profile_image, result.education_institutions, result.education_majors, result.education_degrees, result.graduation_date, result.identification_option, result.identification_material]

                        #     # create a list of new row
                        #     row = [firstName, midName, lastName, age, birthDay, firstAddress, secondAddress, city, province, country, postalCode, gender, religion, profile_image, education_institution, education_majors, education_degrees, graduation_date, identification_option, identification_material]

                        #     j = 0
                        #     # update the user's information
                        #     for i in range(len(columns)):
                        #       columns[i] = row[j]
                        #       j += 1

                        #     # when the data have been updated successfully
                        #     db.session.commit()
                        #     return jsonify({
                        #       'message' : f'Profile for user {username} has been updated successfully!'
                        #       }), 201

                        #   # catch the server error and return an internal server error code
                        #   except Exception as e:
                        #     print(f'There is an error while updating the user information!')
                        #     return jsonify({
                        #       'message' : f'User {username} profile cannot be updated due to an internal server error: {e}!'
                        #     }), 500

                        try:
                            # if the users information didn't exist in the database yet
                            # create a list of new user instance
                            new_user = UserInformation(first_name=firstName, middle_name=midName, last_name=lastName, age=age, date_of_birth=birthDay, address_line_1=firstAddress, address_line_2=secondAddress, city=city, province=province, country=country, postal_code=postalCode, gender=gender, religion=religion, profile_image=profile_image, user_bio=user_bio, interests=user_interest, education_institutions=education_institution, education_majors=education_majors, education_degrees=education_degrees, graduation_date=graduation_date, identification_option=identification_option, identification_material=identification_material, user_id=user_id)

                            # add new user into users model
                            db.session.add(new_user)
                            # commit the change to the database -> 201 if successful
                            db.session.commit()

                            response_data = {"message" : f"User's information has been added successfully!"}
                            response_json = json.dumps(response_data)
                            response = Response(
                                response=response_json,
                                status=HTTPStatus.CREATED,
                                mimetype="application/json"
                            )
                            return response

                        # if there is an error with the server (Internal server error) -> 500
                        except Exception as e:
                            db.session.rollback()
                            response_data = {
                                "message": f"Cannot add the profile for user with user_id: {user_id} into the database",
                                "error": f"{e}"
                            }
                            response_json = json.dumps(response_data)
                            response = Response(
                                response=response_json,
                                status=500,
                                mimetype="application/json",
                            )
                            return response

                    # if there is any invalid field is being caught (including address, profile image(if any)), send the error to the client with a 400 bad request status
                    else:
                        db.session.rollback()
                        response_data = {
                            "message": f"Caught invalid client fields!",
                            "errors": errors,  # errors that are caught with the invalid fields -> users need to enter them again
                        }
                        response_json = json.dumps(response_data)
                        response = Response(
                            response=response_json,
                            status=400,
                            mimetype="application/json",
                        )
                        return response

                # catch the error if there is an internal server error
                except Exception as e:
                    db.session.rollback()
                    response_data = {
                        "message": f"There is an internal server error: {e}"
                    }
                    response_json = json.dumps(response_data)
                    response = Response(
                        response=response_json, status=500, mimetype="application/json"
                    )
                    return response

    # a method to handle the UPDATE request
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    def patch(self):
        with user_profile_app.app_context():
            # get the request method
            if request.method == 'PATCH':
                try:
                    # get the token from cookies
                    token = request.cookies.get('token')
                    # decode the token
                    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
                    user_id = decoded_token['id']
                    # query the user_information table to see if the user id already has profile
                    user = UserInformation.query.filter_by(user_id=user_id).first()

                    if not user: # -> if the user didn't have any profile record
                        abort(404, {
                            'message' : f'Sorry! User profile does not exist, cannot update.'
                        })

                    # get the user's input from the form data
                    update_form_data = reqparse.RequestParser()
                    self.__formData_addArguments(update_form_data)

                    # parse the arguments from the form data
                    update_args = update_form_data.parse_args()

                    # create an errors dictionary to catch the error from the form data
                    errors = {}

                    # check if each argument is in the update_args -> yes (update the database field), no (leave them)
                    all_request_fields = ['firstName', 'midName', 'lastName', 'age', 'birthDay', 'firstAddress', 'secondAddress', 'city', 'province', 'country', 'postalCode', 'gender', 'profile_image', 'religion', 'user_bio', 'user_interest', 'education_institutions', 'education_majors', 'education_degrees', 'graduation_date', 'identification_option', 'identification_material']
                    all_model_fields = [user.first_name, user.middle_name, user.last_name, user.age, user.date_of_birth, user.address_line_1, user.address_line_2, user.city, user.province, user.country, user.postal_code, user.gender, user.profile_image, user.religion, user.user_bio, user.interests, user.education_institutions, user.education_majors, user.education_degrees, user.graduation_date, user.identification_option, user.identification_material]

                    # validate each input field
                    validate_users_information(
                        errors,
                        update_args['firstName'],
                        update_args['lastName'],
                        update_args['age'],
                        update_args['birthDay'],
                        update_args['gender'],
                        update_args['profile_image'],
                        update_args['education_institutions'],
                        update_args['education_majors'],
                        update_args['education_degrees'],
                        update_args['graduation_date'],
                        update_args['identification_option'],
                        update_args['identification_material']
                    )

                    # check to see if the address is corrected
                    geolocation_api_result = checkAddress(
                        errors,
                        update_args['firstAddress'],
                        update_args['city'],
                        update_args['province'],
                        update_args['country'],
                        update_args['postalCode'],
                        update_args['secondAddress']
                    )

                    # if all the fields are valid
                    if not errors and geolocation_api_result.is_valid_address():
                        j = 0
                        for i in range(len(all_request_fields)):
                            if update_args[all_request_fields[i]]:
                                all_model_fields[j] = update_args[all_request_fields[i]]
                                # commit the database insertion after update the fields
                                db.session.commit()
                            j += 1

                        # return a response to the user
                        response_data = ({
                            'message' : f'Successfully update the user information to the database!'
                        })
                        response_json = json.dumps(response_data)
                        response = Response(response_json, status=HTTPStatus.CREATED, mimetype='application/json')
                        return response
                    else:
                        raise ValueError
                except ValueError:
                    response_data = ({
                        'message' : 'Caught invalid client fields!',
                        'errors' : errors # send the errors to the client
                    })
                    response_json = json.dumps(response_data)
                    response = Response(response_json, status=400, mimetype='application/json')
                    return response

                except Exception as error:
                    response_data = ({
                        'message' : f'There is an internal server error while updating user information',
                        'server_errors' : error
                    })
                    response_json = json.dumps(response_data)
                    response = Response(response_json, status=500, mimetype='application/json')
                    return response


    # a method to delete a user's profile
