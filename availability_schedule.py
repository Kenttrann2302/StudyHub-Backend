# THIS IS THE REST API FOR CRUD OPERATIONS FOR GETTING THE USERS AVALABILTY SCHEDULE
# import libraries
import json
import pdb
from http import HTTPStatus
from werkzeug.exceptions import Conflict, BadRequest, NotFound

import jwt
from flask import Flask, Response, jsonify, request, current_app
from flask_migrate import Migrate
from flask_restful import Resource, inputs, reqparse, fields, marshal_with, abort
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from marshmallow import Schema

# import other files in the root directory
from database.users_models import AvailabilitySchedule, db
from get_env import secret_key
from helper_functions.middleware_functions import token_required

# resource fields to serialize the object
_availabilty_schedule_resource_fields = {
    "timezone": fields.String,
    "availability_time": fields.String  # example of what this field might look like:
    # "Monday : (5a.m. - 8a.m.), (3p.m. - 6p.m.); Tuesday : (8a.m. - 10 a.m.), ..."
    # Days are seperated by semicolons, time frames for each day are seperated by commas and day vs time frames are seperated by colons
}


# REST API for CRUD for user to interact with availabilty schedule resources
class AvailabilityScheduleResource(Resource):
    # private method that abort if user's availabilty schedule record has a conflict
    def __abort_if_schedule_exists(self, user_id) -> None:
        if user_id:
            raise Conflict
        return

    # private method that abort if user didn't have availabilty schedule to update or delete
    def __abort_if_schedule_does_not_exists(self, user_id) -> None:
        if not user_id:
            raise NotFound
        return

    # private method to add arguments into the form data
    def __post_form_data_add_arguments(self, post_form_data) -> None:
        post_form_data.add_argument(
            "timezone",
            type=str,
            help="This timezone can be achieved by the Google API",
            required=True,
        )

        post_form_data.add_argument(
            "availability_time",
            type=str,
            help="Student has to choose their availabilty schedule",
            required=True,
        )

    # a private method that parse the update form data
    def __update_form_data_add_argument(self, update_form_data) -> None:
        update_form_data.add_argument("timezone", type=str)
        update_form_data.add_argument("availability_time", type=str)

    # a private method to validate the user input data before inserting
    def __validate_form_data(self, errors, **kwargs) -> None:
        for key, value in kwargs.items():
            # validate timezone
            if key == "timezone" and value:
                # if the value is null
                if value == "" or value == "None" or value == "Null":
                    print("Timezone can not be null")
                    errors[key] = f"Student must have their timezone"
            # validate avalabilty schedule
            else:
                if value == "" or value == "None" or value == "Null":
                    print("Schedule cannot be null")
                    errors[key] = f"Student must have their availability schedule"
        return

    # a GET method to get the user availabilty schedule from the database and return it to the client
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
            "can_view_availabilty_schedule",
            "can_change_availabilty_schedule",
        ],
        secret_key=secret_key,
    )
    @marshal_with(
        _availabilty_schedule_resource_fields
    )  # serialize the response object
    def get(self):
        with current_app.app_context():
            try:
                # get the token from cookies
                token = request.cookies.get("token")
                # decode the token to get the user information
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_information_id = decoded_token["user_information_id"]
                # query the availability schedule table to get the user with user id
                user_availabilty_schedule = AvailabilitySchedule.query.filter_by(
                    user_id=user_information_id
                ).first()

                # if the user record for availabilty schedule is not found
                self.__abort_if_schedule_does_not_exists(user_availabilty_schedule)

                # if the user record for availabilty schedule is found
                return user_availabilty_schedule, HTTPStatus.OK

            except NotFound as not_found_error:  # try to catch the not found error
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            except Exception as server_error:  # try to catch any internal server error
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

    # a POST method to create user availabity schedule
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
            "can_view_availabilty_schedule",
            "can_change_availabilty_schedule",
        ],
        secret_key=secret_key,
    )
    @marshal_with(
        _availabilty_schedule_resource_fields
    )  # serialize the response object
    def post(self):
        with current_app.app_context():
            # get the token from cookies
            try:
                # Intialize the errors dictionary to store the errors from the form data
                errors = {}

                token = request.cookies.get("token")
                # decode the token to get the user information
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_information_id = decoded_token["user_information_id"]

                # get the users input from the post form data
                post_form_data = reqparse.RequestParser()
                self.__post_form_data_add_arguments(
                    post_form_data=post_form_data
                )  # add all the arguments

                args = post_form_data.parse_args()  # parse all the form data fields
                timezone = args["timezone"]
                availability_time = args["availability_time"]

                # Validate the form data
                self.__validate_form_data(errors, **args)

                # if no errors found in the form data
                if not errors:
                    # query the database to check if this user already has the availabilty schedule
                    result = AvailabilitySchedule.query.filter_by(
                        user_id=user_information_id
                    ).first()

                    # abort if the result is True
                    self.__abort_if_schedule_exists(result)

                    # if the user didn't have any availabilty schedule record
                    # create a list of new availabilty schedule for user
                    new_availabilty_schedule = AvailabilitySchedule(
                        user_id=user_information_id,
                        timezone=timezone,
                        availability_time=availability_time,
                    )

                    # add new study preferences for this user to the database
                    db.session.add(new_availabilty_schedule)

                    db.session.commit()

                    # query the user availabilty schedule in order to serialize the response to the client
                    query_user_availabilty_schedule = (
                        AvailabilitySchedule.query.filter_by(
                            user_id=user_information_id
                        ).first()
                    )

                    return query_user_availabilty_schedule, HTTPStatus.CREATED

                # if there are errors in the form data
                else:
                    raise BadRequest

            # catch the Value Error
            except BadRequest as bad_request_error:
                db.session.rollback()
                abort(HTTPStatus.BAD_REQUEST, message=json.dumps(errors))

            # catch the 409 Conflict Error
            except Conflict as conflict_error:
                db.session.rollback()
                abort(HTTPStatus.CONFLICT, message=f"{conflict_error}")

            # catch the server error
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

    # a PATCH method to update the user availabilty schedule
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
            "can_view_availabilty_schedule",
            "can_change_availabilty_schedule",
        ],
        secret_key=secret_key,
    )
    @marshal_with(
        _availabilty_schedule_resource_fields
    )  # serialize the response object
    def patch(self):
        with current_app.app_context():
            # get the token from cookies
            try:
                # initialize an empty errors dictionary to catch the client side errors
                errors = {}

                token = request.cookies.get("token")
                # decode the token to get the user's availabilty schedule
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                # get the user_id from the token
                user_information_id = decoded_token["user_information_id"]
                # query the availabilty schedule table to see if this user already have the record to change
                user_availability_schedule = AvailabilitySchedule.query.filter_by(
                    user_id=user_information_id
                ).first()

                # if no user availabilty schedule found
                self.__abort_if_schedule_does_not_exists(user_availability_schedule)

                # get the user's input from the form data
                update_form_data = reqparse.RequestParser()
                # add the arguments to the form data
                self.__update_form_data_add_argument(update_form_data)

                # parse the arguments from the form data
                update_args = update_form_data.parse_args()

                # validate the update form data
                self.__validate_form_data(errors, **update_args)

                # if all the fields are valid
                if not errors:
                    for args_names, args_value in update_args.items():
                        if args_value:
                            setattr(user_availability_schedule, args_names, args_value)

                    # commit the change to the database
                    db.session.commit()

                    # query the database to get the information of the user after updating
                    update_user = AvailabilitySchedule.query.filter_by(
                        user_id=user_information_id
                    ).first()

                    # return a response to the client
                    return update_user, HTTPStatus.CREATED

                # raise the Value Error if any client field is invalid
                else:
                    raise BadRequest

            except BadRequest as bad_request_error:  # catch any 400 Bad Request
                db.session.rollback()
                abort(HTTPStatus.BAD_REQUEST, message=json.dumps(errors))

            # catch the 404 user's record not found error
            except NotFound as not_found_error:
                db.session.rollback()
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            # catch any server error
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

    # a DELETE method to delete the availabilty schedule record
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_availabilty_schedule_resource_fields)
    def delete(self):
        with current_app.app_context():
            # get the token from cookies
            try:
                token = request.cookies.get("token")
                decoded_token = jwt.decode(
                    token, secret_key, algorithms=["HS256"]
                )  # decode the jwt token
                # get the user id
                user_information_id = decoded_token["user_information_id"]

                # query the database to see if the user has the record of availabilty schedule
                user_availabilty_schedule = AvailabilitySchedule.query.filter_by(
                    user_id=user_information_id
                ).first()

                # abort if no record found
                self.__abort_if_schedule_does_not_exists(user_availabilty_schedule)

                db.session.query(AvailabilitySchedule).filter(
                    AvailabilitySchedule.user_id == user_information_id
                ).delete()

                # commit the change to the database
                db.session.commit()

                # return the response to the client if there is no error occured
                response_data = {
                    "message": f"User availabilty schedule has been successfully deleted!"
                }
                response_json = json.dumps(response_data)
                response = Response(
                    response_json,
                    status=HTTPStatus.CREATED,
                    mimetype="application/json",
                )
                return response

            # except 404 not found error
            except NotFound as not_found_error:
                db.session.rollback()
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            # except the internal server error
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")
