# Here are the models that store the users profiles information (most important)

# import libraries
import json
import uuid
from datetime import datetime

import pytz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

# create a db instance
db = SQLAlchemy()


################################## USER'S ACCOUNT REGISTRATION MODEL ##################################
# Define a registration table to store the user's id, username (email), password, phone_number (for more authentication)
class Users(db.Model):
    __tablename__ = "users"

    user_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )  # using universal unique identifier for best security practice
    username = db.Column(db.String(500), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False, unique=True)
    verification_method = db.Column(
        db.Enum(
            "--select--",
            "Email",
            "Phone number",
            "Device Push Notification",
            name="verification_options",
        ),
        nullable=False,
    )  # duo factor authentication methods such as Email, SMS or Device Push Notification
    verification = db.Column(
        db.String(500), nullable=False
    )  # a field to store the user's email or sms or device number depends on the verification_method
    account_verified = db.Column(db.Boolean, nullable=False, default=False)
    temp_token = db.Column(
        db.String(500), nullable=True
    )  # a field to store a temporary token that is generated to verify the user's verification
    is_active = db.Column(
        db.Boolean, nullable=False, default=False
    )  # deactivate the user's account when they violate the terms and condition or they lock their account
    profile = db.relationship(
        "UserInformation", uselist=False, backref="users"
    )  # perform a 1 to 1 relationship with the user's profile
    permissions = db.relationship(
        "Permission", backref="users", lazy=True
    )  # perform a 1 to many relationship with the user's permission model
    created_at = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("EST")), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(pytz.timezone("EST")),
        onupdate=datetime.now(pytz.timezone("EST")),
        nullable=False,
    )

    def __repr__(self) -> str:
        return "<Users %r>" % self.user_id % self.username


# Define a permission table to have one-to-many relationship to registration table
class Permission(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.user_id"), nullable=False
    )


################################### USER'S PROFILE MODEL ###################################
# a list of majors in university
with open("database/json/majors.json", "r") as f:
    data = json.load(f)

list_of_majors = []

for i in range(55):
    list_of_majors.append(data["majors"][f"major{i}"])


# Define a user table to store the user's data when they sign up for the saving challenges algorithm
class UserInformation(db.Model):
    __tablename__ = "user_information"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    profile_image = db.Column(
        db.String(500), nullable=True
    )  # allow users to add the profile picture
    user_bio = db.Column(
        db.Text, nullable=True
    )  # allow user to update their bio information
    interests = db.Column(
        db.Text, nullable=True
    )  # allow user to update their interests
    activity_status = db.Column(db.String(20), default="offline")
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address_line_1 = db.Column(db.String(500), nullable=False)
    address_line_2 = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(
        db.String(10), nullable=False
    )  # Geolocation API will be used to validate the address
    timezone = db.Column(
        db.String(50), nullable=True
    )  # this timezone will be retrieved by Google Timezone API
    gender = db.Column(
        db.Enum(
            "--select--",
            "Male",
            "Female",
            "Others",
            "Prefer not to tell",
            name="gender_options",
        ),
        nullable=False,
    )
    religion = db.Column(db.String(100), nullable=True)
    education_institutions = db.Column(
        db.Enum(
            "--select--",
            "University of Waterloo",
            "University of Toronto",
            "University of British Columbia",
            name="universities",
        ),
        nullable=False,
    )  # a list of universities and colleges options that StudyHub currently support
    education_majors = db.Column(
        db.Enum(*list_of_majors, name="majors_lists"), nullable=False
    )
    # a list of majors in universities that StudyHub currently support
    education_degrees = db.Column(
        db.Enum(
            "--select--",
            "Associate's Degree",
            "Bachelor's Degree",
            "Master's Degree",
            "Doctoral Degree",
            "Professional Degree",
            name="degree_levels",
        ),
        nullable=False,
    )
    graduation_date = db.Column(db.Date, nullable=False)
    # user's proof of enrollment
    identification_option = db.Column(
        db.Enum(
            "--select--",
            "Student Email Address",
            "Student ID Card",
            "Enrollment Verification Letter",
            "Transcript",
            name="student_identification",
        ),
        nullable=False,
    )
    identification_material = db.Column(
        db.String(500), nullable=False
    )  # image of identification that related to the user's school
    created_at = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("EST")), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(pytz.timezone("EST")),
        onupdate=datetime.now(pytz.timezone("EST")),
        nullable=False,
    )

    # relationship
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.user_id"), nullable=False
    )  # form a one-to-one relationship with the user's id in the users table (using foreign key contraint)

    study_preferences = db.relationship(
        "StudyPreferences", backref="user_information", uselist=False, lazy=True
    )

    availabity_schedule = db.relationship(
        "AvailabilitySchedule", backref="user_information", uselist=False, lazy=True
    )

    def __repr__(self):
        return "<Users %r>" % self.first_name % self.last_name


########################## STUDY PREFERENCES IN USER'S PROFILE #############################
# read in the json files
with open("database/json/study_env.json", "r") as f2:
    study_env = json.load(f2)

with open("database/json/study_time.json", "r") as f3:
    study_time = json.load(f3)

with open("database/json/time_management_methods.json", "r") as f4:
    time_management_methods = json.load(f4)

with open("database/json/study_techniques.json", "r") as f5:
    study_techniques = json.load(f5)

with open("database/json/social_media.json", "r") as f6:
    social_media_platforms = json.load(f6)

list_study_env = []
list_study_time = []
list_time_management_methods = []
list_study_techniques = []
list_social_media = []

# append the list of the study environment and study time frame
for i in range(12):
    list_study_env.append(study_env["Study_env_preferences"][f"{i+1}"])
    list_study_time.append(
        study_time["Study_time_preferences"][f"{i+1}"]["Time"]
        + "-"
        + study_time["Study_time_preferences"][f"{i+1}"]["Frame"]
    )

# append the list of time management methods and study techniques
for i in range(3):
    list_time_management_methods.append(
        time_management_methods["Time_Management_Methods"][f"Method{i+1}"]["name"]
    )

for i in range(14):
    list_study_techniques.append(
        study_techniques["Study_Techniques"][f"technique{i+1}"]["name"]
    )

# append the list of social media platforms that are supported in StudyHub
for i in range(20):
    list_social_media.append(social_media_platforms["Social_media_platforms"][f"{i+1}"])


# Define a study preferences model to store the user's study preference and habits
# This model will perform a one to one relationship with the users profile -> one user will have one study preference for the k-means clustering algorithm
class StudyPreferences(db.Model):
    __tablename__ = "study_preferences"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("user_information.id"), nullable=False
    )  # form a one to one relationship with the user's profile

    # study environment preferences
    study_env_prefereces = db.Column(
        db.Enum(*list_study_env, name="list_study_env"), nullable=False
    )

    # study time preferences
    study_time_preferences = db.Column(
        db.Enum(*list_study_time, name="list_study_time"), nullable=False
    )

    # study time management methods
    time_management_preferences = db.Column(
        db.Enum(*list_time_management_methods, name="list_time_management_methods"),
        nullable=False,
    )

    # study techniques preferences
    study_techniques_preferences = db.Column(
        db.Enum(*list_study_techniques, name="list_study_techniques"), nullable=False
    )

    # courses preferences
    courses_preferences = db.Column(
        db.ARRAY(db.String(10), dimensions=8), nullable=False
    )  # user can choose up to 8 favorite courses

    # favorite communication social media platform -> connect with people that will be matched to form a study group
    communication_prefereces = db.Column(
        db.Enum(*list_social_media, name="list_social_media"), nullable=False
    )

    created_at = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("EST")), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(pytz.timezone("EST")),
        onupdate=datetime.now(pytz.timezone("EST")),
        nullable=False,
    )

    def __repr__(self) -> str:
        return "<Study Preference %r>" % self.id


################################# AVAILABILITY (USER'S TIME SCHEDULE IN USER'S PROFILE) #################################
# Define a model stores the user's availability or time schedule for best matching result
class AvailabilitySchedule(db.Model):
    __tablename__ = "availability_schedule"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("user_information.id"), nullable=False
    )
    timezone = db.Column(db.Integer, nullable=False)
    schedule = db.Column(
        db.JSON, nullable=False
    )  # a json object that stores the user's weekly schedule, with each day of the week represented as a key and list of time ranges as the value
    preferred_times = db.Column(
        db.JSON, nullable=False
    )  # a json object that stores the user's preferred study times, with each time represented as a key and a boolean value indicating whether the user is avalable at that time
    created_at = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("EST")), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(pytz.timezone("EST")),
        onupdate=datetime.now(pytz.timezone("EST")),
        nullable=False,
    )

    def __repr__(self) -> str:
        return "<Availability Schedule %r" % self.id


############## STUDY GROUP SESSION HISTORY ###############
# Define a model that stores the user's history study group session
# query the group databases that contains the users profile
# class StudyHistory(db.Model):
#   id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
#   user_id = db.Column(db.String(500), db.ForeignKey('user_information.id'), nullable=False)
#   group_id = db.Column(db.String(500), db.ForeignKey())
