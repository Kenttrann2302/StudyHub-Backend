# THIS IS REST API FOR CRUD METHODS FOR STUDY PREFERENCES DATA
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
from database.users_models import StudyPreferences, db
from get_env import secret_key
from helper_functions.middleware_functions import token_required


# resources fields to serialize the response object
_study_preferences_resource_fields = {
    "study_env_preferences": fields.String,
    "study_time_preferences": fields.String,
    "time_management_preferences": fields.String,
    "study_techniques_preferences": fields.String,
    "courses_preferences": fields.String,
    "communication_preferences": fields.String,
}


# REST API for CRUD for user to interact with Study Preferences resources
class StudyPreferencesResource(Resource):
    # private method that abort if user's study preferences record has already existed in the database -> post
    def __abort_if_user_profile_exists(self, user_id) -> None:
        if user_id:
            raise Conflict
        return

    # private method that abort if user didn't have study preferences record -> get, patch, delete
    def __abort_if_user_profile_does_not_exists(self, user_id) -> None:
        if not user_id:
            raise NotFound
        return

    # private method to add arguments into the form data
    def __post_form_data_add_arguments(self, post_form_data) -> None:
        post_form_data.add_argument(
            "study_env_preferences",
            type=str,
            help="Student has to choose their favorite study environment.",
            required=True,
        )

        post_form_data.add_argument(
            "study_time_preferences",
            type=str,
            help="Student has to choose their study time.",
            required=True,
        )

        post_form_data.add_argument(
            "time_management_preferences",
            type=str,
            help="Student has to choose their favorite technique of managing the study session time.",
            required=True,
        )

        post_form_data.add_argument(
            "study_techniques_preferences",
            type=str,
            help="Student has to choose their favorite studying technique.",
            required=True,
        )

        post_form_data.add_argument(
            "courses_preferences",
            type=str,
            help="Student has to choose the maximum of 8 courses",
            required=True,
        )

        post_form_data.add_argument(
            "communication_preferences",
            type=str,
            help="Student has to choose one of the communication methods",
            required=True,
        )

    # a private method that parse the update form data
    def __update_form_data_add_argument(self, update_form_data) -> None:
        update_form_data.add_argument("study_env_preferences", type=str)
        update_form_data.add_argument("study_time_preferences", type=str)
        update_form_data.add_argument("time_management_preferences", type=str)
        update_form_data.add_argument("study_techniques_preferences", type=str)
        update_form_data.add_argument("courses_preferences", type=str)
        update_form_data.add_argument("communication_preferences", type=str)

    # a private method to validate the user input data before inserting them into the database
    def __validate_form_data(self, errors, **kwargs) -> None:
        for key, value in kwargs.items():
            if key == "courses_preferences" and value:
                # split the string into an array of string represents courses codes
                course_count = value.split(", ")
                if len(course_count) > 8:
                    errors[key] = f"Student must choose at most 8 favorite courses."
                elif len(course_count) < 1:
                    errors[key] = f"Student must choose at least 1 favorite course."
            else:
                if value == "--select--":
                    errors[
                        key
                    ] = f"Student must choose one of the following options for {key}"
        return

    # a GET method to get the user study preferences from the database and return it to the client
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
            "can_view_study_preferences",
            "can_change_study_preferences",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_study_preferences_resource_fields)  # serialize the return object
    def get(self):
        with current_app.app_context():
            try:
                # get the token from cookies
                token = request.cookies.get("token")
                # decode the token to get the user information
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_information_id = decoded_token["user_information_id"]
                # query the study preferences table to get the user with the user id
                user_study_pref = StudyPreferences.query.filter_by(
                    user_id=user_information_id
                ).first()

                # if user record for study preferences is not found
                self.__abort_if_user_profile_does_not_exists(user_study_pref)

                # if user record for study preferences found
                return user_study_pref, HTTPStatus.OK

            except (
                NotFound
            ) as not_found_error:  # try to catch the not found error (no user's record found!)
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            except Exception as server_error:  # try to catch any internal server error
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

    # a POST method to get the user study preferences from the form data that was sent by the client
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
            "can_view_study_preferences",
            "can_change_study_preferences",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_study_preferences_resource_fields)  # serialize the return object
    def post(self):
        with current_app.app_context():
            # get the token from cookies
            try:
                token = request.cookies.get("token")
                # decode the token to get the user information
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_information_id = decoded_token["user_information_id"]
                # get the users input from the post form data

                post_form_data = reqparse.RequestParser()
                self.__post_form_data_add_arguments(
                    post_form_data
                )  # add all the arguments

                args = post_form_data.parse_args()  # parse all the form data fields
                study_env_pref = args["study_env_preferences"]
                study_time_pref = args["study_time_preferences"]
                time_management_pref = args["time_management_preferences"]
                study_techniques_pref = args["study_techniques_preferences"]
                courses_pref = args["courses_preferences"]
                communication_pref = args["communication_preferences"]

                # Initialize the errors dictionary to store the errors from the form data
                errors = {}

                # Validate the form data, if not -> send the error messages to front-end
                # validate the users input before inserting the data into the database
                self.__validate_form_data(errors, **args)

                pdb.set_trace()
                # if no errors found in the form data
                if not errors:
                    # query the database to check if there is any user that already exists with the same id
                    result = StudyPreferences.query.filter_by(
                        user_id=user_information_id
                    ).first()

                    # abort if the result is already in the database -> has to use update method
                    self.__abort_if_user_profile_exists(result)

                    # if the user didn't have any study preferences record
                    # create a list of new study preferences for user
                    new_study_preferences = StudyPreferences(
                        user_id=user_information_id,
                        study_env_preferences=study_env_pref,
                        study_time_preferences=study_time_pref,
                        time_management_preferences=time_management_pref,
                        study_techniques_preferences=study_techniques_pref,
                        courses_preferences=courses_pref,
                        communication_preferences=communication_pref,
                    )

                    # add new study preferences for this user to the database
                    db.session.add(new_study_preferences)

                    db.session.commit()

                    # query the user study preferences in order to serialize the response to the client
                    query_user_study_preferences = StudyPreferences.query.filter_by(
                        user_id=user_information_id
                    ).first()

                    return query_user_study_preferences, HTTPStatus.CREATED

                # if there are errors in the form data
                else:
                    raise BadRequest

            # catch the Value Error
            except BadRequest as bad_request_error:
                db.session.rollback()
                abort(HTTPStatus.BAD_REQUEST, message=json.dumps(errors))

            # catch the 409 conflict error
            except Conflict as conflict_error:
                db.session.rollback()
                abort(HTTPStatus.CONFLICT, message=f"{conflict_error}")

            # catch the server error
            except Exception as server_error:
                db.session.rollback
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

    # a PATCH method to update the user study preferences from the update form data that was sent by the client
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
            "can_view_study_preferences",
            "can_change_study_preferences",
        ],
        secret_key=secret_key,
    )
    @marshal_with(
        _study_preferences_resource_fields
    )  # serialize the response object to front-end
    def patch(self):
        with current_app.app_context():
            # get the token from cookies
            try:
                token = request.cookies.get("token")
                # decode the token to get the user's study preferences
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                # get the user_id from the token
                user_information_id = decoded_token["user_information_id"]
                # query the study preferences table to see if the user's study preferences record has already been in the database
                user_study_pref = StudyPreferences.query.filter_by(
                    user_id=user_information_id
                ).first()

                # if no user study preference record found
                self.__abort_if_user_profile_does_not_exists(user_study_pref)

                # get the user's input from the form data
                update_form_data = reqparse.RequestParser()
                # add the arguments to the form data
                self.__update_form_data_add_argument(update_form_data)

                # parse the arguments from the form data
                update_args = update_form_data.parse_args()

                # initialize an empty errors dictionary to catch the client field error
                errors = {}

                # check if each argument is in the update_args -> if yes -> update the database field, if no -> leave

                self.__validate_form_data(errors, **update_args)

                # if all the fields are valid
                if not errors:
                    for args_names, args_values in update_args.items():
                        if args_values:
                            setattr(user_study_pref, args_names, args_values)

                    # commit the change to the database
                    db.session.commit()

                    # query the database to get the information of the user after updating
                    update_user = StudyPreferences.query.filter_by(
                        user_id=user_information_id
                    ).first()

                    # return a response to the client
                    return update_user, HTTPStatus.CREATED

                # raise Value Error if any client field is invalid
                else:
                    raise BadRequest

            except BadRequest as bad_request_error:  # catch any 400 bad request error
                db.session.rollback()
                abort(HTTPStatus.BAD_REQUEST, message=json.dumps(errors))

            # catch the 404 user's study preferences record not found error
            except NotFound as not_found_error:
                db.session.rollback()
                abort(HTTPStatus.NOT_FOUND, message=f"{not_found_error}")

            # catch any server error
            except Exception as server_error:
                db.session.rollback()
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=f"{server_error}")

    # a DELETE method to delete the study preferences record
    @token_required(
        permission_list=[
            "can_view_dashboard",
            "can_view_profile",
            "can_change_profile",
        ],
        secret_key=secret_key,
    )
    @marshal_with(_study_preferences_resource_fields)
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

                # query the database to see if the user has the study preferences
                user_study_pref = StudyPreferences.query.filter_by(
                    user_id=user_information_id
                ).first()

                # abort if no profile found
                self.__abort_if_user_profile_does_not_exists(user_study_pref)

                db.session.query(StudyPreferences).filter(
                    StudyPreferences.user_id == user_information_id
                ).delete()

                # commit the change to the database
                db.session.commit()

                # return the response to the client if there is no error occured
                response_data = {
                    "message": f"User study preference has been successfully deleted!"
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
