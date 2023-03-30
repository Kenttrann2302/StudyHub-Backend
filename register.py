############### REGISTER PAGE FOR USERS TO CREATE THEIR USERNAME AND PASSWORD FOR THE APPLICATION
# import libraries
from flask import Flask, redirect, url_for, session, render_template, request, abort, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
import bcrypt
import boto3
import os
import jwt
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
import pdb

# load in the sensitive data from .env
from dotenv import load_dotenv
# Load the configuration data from the .env file
load_dotenv()

# import the users models from the models.py
from database.users_models import db, Users, Verification
from AWS.aws_sns_helper_function import AWS_SNS_SDKs_setup

# import other files
from helper_functions.users_tables_create import create_registration_table
from helper_functions.registerformValidation import validate_registration_form
from helper_functions.signupformValidations import create_validated_fields_dict

register_app = Flask(__name__)
register_app.config['SERVER_NAME'] = 'localhost:5000'
register_app.config['APPLICATION_ROOT'] = '/'
register_app.config['PREFERRED_URL_SCHEME'] = 'http'
register_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# get the database connection information
database_type = os.getenv("DB_TYPE")
database_host = os.getenv("DB_HOST")
database_username = os.getenv("DB_USER")
database_password = os.getenv("DB_PASS")
database_port = os.getenv("PORT")
database_name = os.getenv("DB_NAME")

# set up the app for testing api
api = Api(register_app)

# register the app instance with the endpoints we are using for this app
registration_routes = Blueprint('registration_routes', __name__)

# Add a test configuration
register_app.config['TESTING'] = True
register_app.config['WTF_CSRF_ENABLED'] = False

migrate = Migrate(register_app, db)

# connect to the userdatabase where will store all the users data
register_app.config['SQLALCHEMY_DATABASE_URI'] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
engine = create_engine(f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}")
inspector = Inspector.from_engine(engine)

# create the sqlalchemy database object 
db.init_app(register_app)

# create the registration table according to the registration model
create_registration_table(app=register_app, inspector=inspector, db=db, engine=engine)

# global variables
# initialize all the a dictionary of validated fields for user inputs
validated_fields = {
  'firstName' : '',
  'midName' : '',
  'lastName' : '',
  'age' : '',
  'birthDay' : '',
  'firstAddress' : '',
  'secondAddress' : '',
  'city' : '',
  'province' : '',
  'country' : '',
  'postalCode' : '',
  'gender' : '',
  'religion' : '',
  'verification' : '',
  'verification_material' : '',
  'username' : '',
  'password' : '',
  'password_confirmation' : '',
  'verification_id' : '',
  'verification_method' : ''
}

# initialize the errors dictionary in order to store the errors for each input fields
register_errors = {}

# create a resource for rest api to handle the post request to the verification database
class VerificationMethodsResource(Resource):
 def __init__(self) -> None:
   super().__init__()

 # this is a helper function inserting the multi-factor registration methods into the table
 def insert_verification_table(self) -> None:
  with register_app.app_context():
    # create an instance of verification methods
    new_verification_methods = [
      Verification(id=1, verification_options='--select--'),
      Verification(id=2, verification_options='Email'),
      Verification(id=3, verification_options='Phone Number')
    ]

    # add new verification methods serializer into the database
    for verification in new_verification_methods:
      try:
        db.session.add(verification)
        # commit the change to the database
        db.session.commit()
        print(f"Verification method {verification.verification_options} added successfully!")
      except:
        db.session.rollback()
        print(f"Verification method {verification.verification_options} already existed in the database!")

 # this is a function to render the register form for users to register for the app
 def registration(self) -> None:
  with register_app.app_context():
   # query the verification database to get all the verification_options
   verification_options = Verification.query.all()

   # call the helper function to get the validated fields with empty strings for each field
   create_validated_fields_dict(validated_fields, firstName='', midName='', lastName='', age='', birthDay='', firstAddress='', secondAdress='', city='', province='', country='', postalCode='', gender='', religion='', verification='', verification_material='', username='', password='', password_confirmation='', verification_id='', verification_method='')

   return render_template("registration.html", verification_options = verification_options, validated_fields=validated_fields)

# define another resource for rest api to handle a post request to the registration database
class RegistrationResource(Resource):
 def __init__(self) -> None:
   super().__init__()
   
 # this is a function to handle the POST request from the registration form and insert the registration fields into the database
 def createAccount(self) -> None:
  with register_app.app_context():
   if request.method == 'POST':
    try: 
      # get the form data and validate them before inserting into the database
      username = request.form['username']
      password = request.form['password']
      password_confirmation = request.form['password-confirmation']
      verification_id = request.form['verification_id']
      areacode_id = request.form['phone-number-areacode']
      verification_method = request.form['verification_method']

      new_user = [username, password, password_confirmation, verification_method]

      # validate the form data, if not -> send error messages to the website
      # validate the users registration input on front-end before inserting the data into the database
      validated_registration = validate_registration_form(new_user=new_user, errors=register_errors, verification_id=verification_id, areacode_id=areacode_id)

      # create a dictionary to store the validated fields by calling the helper function
      create_validated_fields_dict(validated_fields, firstName='', midName='', lastName='', age='', birthDay='', firstAddress='', secondAdress='', city='', province='', country='', postalCode='', gender='', religion='', verification='', verification_material='', username=username, password=password, password_confirmation=password_confirmation, verification_id=verification_id, verification_method=verification_method)

      # handle appropriate validated_registration
      if len(validated_registration) == 4 and len(register_errors) == 0:
        # genrate the salt for the hashed_password
        salt = bcrypt.gensalt()
        # hash the password using bcrypt hashing algorithm 
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        decoded_salt = salt.decode('utf-8')
        decoded_hashed_password = hashed_password.decode('utf-8')

        # query each field to make sure each of them is unique
        username_taken = Users.query.filter(
          Users.username == username
        ).first() is not None

        password_taken = Users.query.filter(
          Users.password == decoded_hashed_password
        ).first() is not None

        verification_method_taken = Users.query.filter(
          Users.verification_id == verification_id,
          Users.verification_method == verification_method
        ).first() is not None

        # check if there is the users input already in the database
        if username_taken:
          register_errors['username'] = f"Sorry! This username already exists!"
          return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)
        elif password_taken:
          register_errors['password'] = f"Sorry! This password already exists!"
          return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)

        elif verification_method_taken:
          switch = {
            int(verification_id) == 2: f"Sorry! This email has been registered in our system!",
            int(verification_id) == 3: f"Sorry! This phone number has been registered in our system!"
          }

          error_message = switch.get(True, 'None')
          if error_message is not None:
            register_errors['verification-input'] = error_message
            return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)

        else:
          # create an instance to add the new user into the database
          add_new_users = [
            Users(username=validated_registration[0], password=decoded_hashed_password, password_salt=decoded_salt , verification_id=int(verification_id), verification_method=validated_registration[3])
          ]

          # add new user to the registration model
          for user in add_new_users:
            try:
              db.session.add(user)
              # commit the change to the database
              db.session.commit()
              print(f"User {user.user_id} added successfully!")
              # Connect with AWS SNS using AWS SDKs to send either an email confirmation or SMS verification to the user's email
              aws_sns_model = AWS_SNS_SDKs_setup()
              # email
              if int(verification_id) == 2:
                response_message = aws_sns_model.send_email_confirmation(email=verification_method)
              else:
                response_message = aws_sns_model.send_sms_confirmation(phone_number=areacode_id + verification_method)
              
              # check if the response_message is sent successfully!
              if response_message is not None:
                return render_template('successRegistration.html', username=username, verification_id=verification_id)
              else:
                raise ValueError(f"Cannot proccess confirmation protocol!")

            except BaseException as error:
              # handle the problem while inserting user registration into the database
              db.session.rollback()
              print(f"Cannot send a confirmation to user {user.user_id}'s {user.verification_method}! There might be some external errors with the server!")
              return jsonify({'message' : 'Error with AWS Client!'}), 400
        
      else:
        raise ValueError(f'There is an error in the form data!')

    # handle the errors if there is any errors when validating the inputs on the form
    except BaseException as error:
      db.session.rollback()
      verification_options = Verification.query.all()
      # re-render the form for users to retype the non-validated fields
      return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)

# add registration resource to rest api
api.add_resource(VerificationMethodsResource, '/scholarsavings/register/')
api.add_resource(RegistrationResource, '/scholarsavings/createaccount/')

# Register the routes
registration_routes.add_url_rule('/scholarsavings/register/', view_func=VerificationMethodsResource.as_view('verification_methods'))
registration_routes.add_url_rule('/scholarsavings/createaccount/', view_func=RegistrationResource.as_view('registration'))

# register the blueprint with the app instance
register_app.register_blueprint(registration_routes)
