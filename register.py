############### REGISTER PAGE FOR USERS TO CREATE THEIR USERNAME AND PASSWORD FOR THE APPLICATION
# import libraries
from flask import Flask, redirect, url_for, session, render_template, request, abort, Blueprint, jsonify, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, reqparse, fields, marshal_with
import bcrypt
import os
import json
import jwt
import requests
import pytz
import random
import time
import secrets
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
import pdb

# import the users models from the models.py
from database.users_models import db, Users

# import third party services for verification method confirmation
from Twilio.twilio_send_email import sendgrid_verification_email

# import other files
from helper_functions.users_tables_create import create_all_tables
from helper_functions.registerformValidation import validate_registration_form
from helper_functions.validate_users_information import create_validated_fields_dict
from get_env import secret_key, database_type, database_host, database_username, database_password, database_port, database_name

register_app = Flask(__name__)
# register_app.config['SERVER_NAME'] = '127.0.0.1:5000'
# register_app.config['APPLICATION_ROOT'] = '/'
# register_app.config['PREFERRED_URL_SCHEME'] = 'http'
# register_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# register_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

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

# # create the sqlalchemy database object 
db.init_app(register_app)

# create the registration table according to the registration model
create_all_tables(app=register_app, inspector=inspector, db=db, engine=engine)

# global variables
# initialize all the a dictionary of validated fields for user inputs
validated_fields = {
  'username' : '',
  'password' : '',
  'password_confirmation' : '',
  'verification_id' : '',
  'verification_method' : ''
}

# initialize the errors dictionary in order to store the errors for each input fields
register_errors = {}

# define a resource fields to serialize the object (user's login information) to make sure that all the identifications have been inserted success
user_resource_fields = {
  'user_id' : fields.String,
  'username' : fields.String,
  'password' : fields.String,
  'verification_method' : fields.String,
  'verification' : fields.String
}

# create a resource for rest api to handle the post request 
class RegistrationResource(Resource):
 def __init__(self) -> None:
   super().__init__()

 # this is a method to handle the GET request from the database after inserting the user's login information into the database
 @marshal_with(user_resource_fields)
 def get(self) -> None:
  with register_app.app_context():
    # get all the users from the database
    try:
      all_users = Users.query.all()
      if all_users:
        return all_users
      else:
        raise ValueError 
    except ValueError:
      response_data = ({
        'message' : f'There is no user has been inserted into the database!'
      })
      response_json = json.dumps(response_data)
      response = Response(response_json, status=404, mimetype="application/json")
      return response
    except Exception as e:
      response_data = ({
        'message' : f'There is an error with the server when querying the database: {e}'
      })
      response_json = json.dumps(response_data)
      response = Response(response_json, status=500, mimetype="application/json")
      return response

 # a function generate a random 6 digits otp code
 def generate_otp(self):
  otp = ''
  for i in range(6):
    otp += str(random.randint(0,9))
  return otp
    
 # this is a function to handle the POST request from the registration form and insert the registration fields into the database
 def post(self) -> None:
  with register_app.app_context():
   if request.method == 'POST':
    try: 
      # get the registration form data and validate them before inserting into the database
      registerForm = reqparse.RequestParser()
      registerForm.add_argument("username", type=str, help="Username is required", required=True)
      registerForm.add_argument("password", type=str, help="Password is required", required=True)
      registerForm.add_argument("password_confirmation", type=str, help="Password confirmation is required", required=True)
      registerForm.add_argument("verification_method", type=str, help="Verification method option is required", required=True)
      registerForm.add_argument("areacode_id", type=str, required=False)
      registerForm.add_argument("verification", type=str, help="Email, SMS or Device Information is required", required=True)

      args = registerForm.parse_args()
      username = args['username']
      password = args['password']
      password_confirmation = args['password_confirmation']
      verification_method = args['verification_method']
      areacode_id = args['areacode_id']
      verification = args['verification']

      new_user = [username, password, password_confirmation, verification]

      # validate the form data, if not -> send error messages to the website
      # validate the users registration input on front-end before inserting the data into the database
      validated_registration = validate_registration_form(new_user=new_user, errors=register_errors, verification_id=verification_method, areacode_id=areacode_id)

      # create a dictionary to store the validated fields by calling the helper function
      create_validated_fields_dict(validated_fields, firstName='', midName='', lastName='', age='', birthDay='', firstAddress='', secondAdress='', city='', province='', country='', postalCode='', gender='', religion='', verification='', verification_material='', username=username, password=password, password_confirmation=password_confirmation, verification_id=verification_method, verification_method=verification)

      # handle appropriate validated_registration
      if len(validated_registration) == 4 and len(register_errors) == 0:
        # genrate the salt for the hashed_password
        salt = bcrypt.gensalt()
        # hash the password using bcrypt hashing algorithm 
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        decoded_hashed_password = hashed_password.decode('utf-8')

        # query each field to make sure each of them is unique
        username_taken = Users.query.filter(
          Users.username == username
        ).first() is not None

        password_taken = Users.query.filter(
          Users.password == decoded_hashed_password
        ).first() is not None

        verification_method_taken = Users.query.filter(
          Users.verification_method == verification_method,
          Users.verification == verification
        ).first() is not None

        # check if there is the users input already in the database
        if username_taken:
          register_errors['username'] = f"Sorry! This username already exists!"
          # return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)
          response_data = ({
            'message' : f'This username has been taken, please choose another username!',
            'error' : register_errors,
            'validated_fields' : validated_fields
          })
          response_json = json.dumps(response_data)
          response = Response(response=response_json, status=409, mimetype="application/json")
          return response

        elif password_taken:
          register_errors['password'] = f"Sorry! This password already exists!"
          # return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)
          response_data = ({
            'message' : f'This password has been taken, please choose another password!',
            'error' : register_errors,
            'validated_fields' : validated_fields
          })
          response_json = json.dumps(response_data)
          response = Response(response=response_json, status=409, mimetype="application/json")
          return response

        elif verification_method_taken:
          switch = {
            verification_method == 'Email': f"Sorry! This email has been registered in our system!",
            verification_method == 'Phone number': f"Sorry! This phone number has been registered in our system!",
            verification_method == 'Device Push Notification' : f"Sorry! This device has been registered in our system!"
          }

          error_message = switch.get(True, 'None')
          if error_message is not None:
            register_errors['verification'] = error_message
            # return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)
            response_data = ({
              'message' : f'This {verification} has been taken! Please choose another email or phone number!',
              'error' : register_errors,
              'validated_fields' : validated_fields
            })
            response_json = json.dumps(response_data)
            response = Response(response=response_json, status=409, mimetype="application/json")
            return response

        else:
          # create an instance to add the new user into the database
          new_user = Users(username=validated_registration[0], password=decoded_hashed_password, verification_method=verification_method, verification=validated_registration[3])
          # add new user to the registration model
          try:
            db.session.add(new_user)
            
            # send a confirmation email to the user to verify their account using Twillio
            if verification_method == 'Email':
              response_status, response_message, temp_token = sendgrid_verification_email(user_email=new_user.verification, studyhub_code=self.generate_otp())

              # store the user's temporary token into the database
              new_user.temp_token = temp_token
              # commit the change to the database
              db.session.commit()

              # check if the response_message is True -> verification sent successfully!
              if response_status and response_message is not None:
                response_data = ({
                  'message1' : f'User with id: {new_user.user_id} has been inserted successfully in to the Users table!',
                  'message2' : f'Sending email confirmation to {verification} successfully!'
                })
                response_json = json.dumps(response_data)
                response = Response(response=response_json, status=201, mimetype='application/json')
                return response

              else:
                raise ValueError(f"Cannot proccess confirmation protocol!")

          except BaseException as error:
            # handle the problem while inserting user registration into the database
            db.session.rollback()
            print(f"Cannot send a confirmation to user {new_user.user_id}'s {new_user.verification}! There might be some external errors with the server!")
            response_data = (
              {'message' : f'Error with Twilio Client: {error}!'}
            )
            response_json = json.dumps(response_data)
            response = Response(response=response_json, status=400, mimetype='application/json')
            return response
        
      else:
        raise ValueError(f'There is an error in the form data!')

    # handle the errors if there is any errors when validating the inputs on the form
    except BaseException as error:
      db.session.rollback()
      # # re-render the form for users to retype the non-validated fields
      # return render_template('registration.html', verification_options=verification_options, errors=register_errors, validated_fields=validated_fields)
      response_data = ({
        'message' : f'User {username} cannot be added due to the internal server error: {error}',
        'error_message' : register_errors,
        'validated_fields' : validated_fields,
        'validated_errors' : register_errors,
      })
      response_json = json.dumps(response_data)
      response = Response(response=response_json, status=500, mimetype='application/json')
      return response
    

# a get request to perform a query string to get the token from the url and decode to get the email address and code to verify the user's email
@registration_routes.route('/studyhub/confirm-email', methods=['GET'])
def email_verifcation():
  try:
    # get the token from the query string
    token = request.args.get('token')

    # decode the token
    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])

    # Check if the expiration time is more than the current time
    exp_time = decoded_token['exp']
    current_time = int(time.time())

    if exp_time > current_time:
      # check if the email address and the temporary token is correct with the record inside the database
      user_email = decoded_token['email']

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
        response_data = ({
          'message' : f"User with email {user_email} has been successfully verified with the system!"
        })
        response_json = json.dumps(response_data)
        response = Response(response=response_json, status=201, mimetype='application/json')
        return response
    
      # if the user email is invalid -> not verified
      else:
        response_data = ({
          'message' : f"User with email {user_email} is not verified and is invalid!"
        })
        response_json = json.dumps(response_data)
        response = Response(response=response_json, status=400, mimetype='application/json')
        return response
  
  except jwt.ExpiredSignatureError:
    # the token has expired
    response_data = ({
      'message' : f'This token has been expired, please generate a new token',
    })
    response_json = json.dumps(response_data)
    response = Response(response=response_json, status=401, mimetype='application/json')
    return response

  except Exception as error:
    response_data = ({
      'message' : f"There is an internal server error while verifying user's email",
      'error' : error
    })
    response_json = json.dumps(response_data)
    response = Response(response=response_json, status=500, mimetype='application/json')
    return response

# add registration resource to rest api
# api.add_resource(RegistrationResource, '/studyhub/createaccount/')

# # Register the routes
# registration_routes.add_url_rule('/studyhub/register/', view_func=VerificationMethodsResource.as_view('verification_methods'))
# registration_routes.add_url_rule('/studyhub/createaccount/', view_func=RegistrationResource.as_view('registration'))

# # register the blueprint with the app instance
# register_app.register_blueprint(registration_routes)
