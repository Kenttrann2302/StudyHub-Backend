# THIS IS REST API FOR CRUD METHODS FOR STUDY PREFERENCES DATA
# import libraries
import json
import pdb
from http import HTTPStatus
from werkzeug.exceptions import Conflict

import jwt
from flask import Flask, Response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Resource, inputs, reqparse, fields, marshal_with, abort
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

# import other files in the root directory
from database.users_models import StudyPreferences, db
from get_env import (
    database_host,
    database_name,
    database_password,
    database_port,
    database_type,
    database_username,
    secret_key
)
from helper_functions.middleware_functions import token_required

# migration config
migrate = Migrate(study_pref_app, db)

# connect flask to postgres database using SQLALCHEMY
study_pref_app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
engine = create_engine(f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}")
inspector = Inspector.from_engine(engine)

# resources fields to serialize the response object
_study_preferences_resource_fields = {
    "user_id" : fields.String,
    "study_env_preferences" : fields.String,
    "study_time_preferences" : fields.String,
    "time_management_preferences" : fields.String,
    "study_techniques_preferences" : fields.String,
    "courses_preferences" : fields.String,
    "communication_preferences" : fields.String
}

# REST API for CRUD for user to interact with Study Preferences resources
class StudyPreference(Resource):
    # private method that abort if user's study preferences record has already existed in the database -> post
    def __abort_if_user_profile_exists(self, user_id) -> None:
        if user_id:
            raise Conflict
        return

    # private method that abort if user didn't have study preferences record -> get, patch, delete
    def __abort_if_user_profile_exists(self, user_id) -> None:
        if not user_id:
            raise Conflict
        return

    # private method to add arguments into the form data
    def __post_form_data_add_arguments(self, post_form_data) -> None:
        post_form_data.add_argument(
            "study_env_preferences",
            type=str,
            help="Student has to choose their favorite study environment.",
            required=True
        )

        post_form_data.add_argument(
            "study_time_preferences",
            type=str,
            help="Student has to choose their study time.",
            required=True
        )

        post_form_data.add_argument(
            "time_management_preferences",
            type=str,
            help="Student has to choose their favorite technique of managing the study session time.",
            required=True
        )

        post_form_data.add_argument(
            "study_techniques_preferences",
            type=str,
            help="Student has to choose their favorite studying technique.",
            required=True
        )

        post_form_data.add_argument(
            "courses_preferences",
            type= fields.List(fields.Nested(fields.String)),
            help="Student has to choose the maximum of 8 courses",
            required=True
        )

        post_form_data.add_argument(
            "communication_preferences",
            type= str,
            help="Student has to choose one of the communication methods",
            required=True
        )

    # a private method that parse the update form data
    # def __update_form_data_add_argument(self, update_form_data) -> None:
    #     update_form_data.add_argument("study_env_preferences")

