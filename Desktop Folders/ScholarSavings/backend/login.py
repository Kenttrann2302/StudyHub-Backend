######################## LOG IN PAGE FOR USERS TO SIGN INTO THEIR ACCOUNT #############
# import libraries
from flask import Flask, redirect, url_for, session, render_template, request, abort, Blueprint, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
import bcrypt
from werkzeug.security import check_password_hash
from sqlalchemy import create_engine
import jwt
import secrets
from datetime import datetime, timedelta
import pdb

# import the users models from the models.py
from database.users_models import db, Users, Verification
from helper_functions.signupformValidations import create_validated_fields_dict

# login app configuration
login_app = Flask(__name__)
login_app.config['SERVER_NAME'] = 'localhost:5000'
login_app.config['APPLICATION_ROOT'] = '/'
login_app.config['PREFERRED_URL_SCHEME'] = 'http'
login_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
login_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# generate random token for secret key
login_app.config['SECRET_KEY'] = secrets.token_hex(16)

# set up the login app for rest api
api = Api(login_app)

db.init_app(login_app)

# register the app instance with the endpoints we are using for this app
login_routes = Blueprint('login_routes', __name__)

# Add an API Test Configuration
login_app.config['TESTING'] = True
login_app.config['WTF_CSRF_ENABLED'] = False

migrate = Migrate(login_app, db)

# connect to the userdatabase where storing all the username, password, email and phone number
login_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
engine = create_engine('postgresql://kenttran@localhost:5432/userdatabase')

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

# create a resource for REST API to handle the GET request that render the form data when the user enter the endpoint to render the login page
class SignInRenderResource(Resource):
 def __init__(self) -> None:
  super().__init__()

 def SignInRender(self):
  with login_app.app_context():
   if request.method == 'GET':
    create_validated_fields_dict(validated_fields=validated_fields, firstName='', midName='', lastName='', age='', birthDay='', firstAddress='', secondAdress='', city='', province='', country='', postalCode='', gender='', religion='', verification='', verification_material='', username='', password='', password_confirmation='', verification_id='', verification_method='')

    return render_template('login.html', validated_fields=validated_fields)
   else:
    # method is not allowed
    abort(405)

# create a resource for REST API to handle the POST request that handle the form data when the user sign in with their username and password
class SignInResource(Resource):
 def __init__(self) -> None:
  super().__init__()

 # this is a function to handle the POST request from the login form data and validate them against the registration table to see if the user is already registered in the system
 def login(self) -> None:
  with login_app.app_context():
   if request.method == 'POST':
    try: 
     # get the form data include username and password and validate them against the database
     signIn_username = request.form['signIn_username']
     signIn_password = request.form['signIn_password']

     # initialize an errors dictionary to notify the error message on the front-end for the user
     signin_errors = {}

     # Get the fields that are validated
     create_validated_fields_dict(validated_fields=validated_fields, firstName='', midName='', lastName='', age='', birthDay='', firstAddress='', secondAdress='', city='', province='', country='', postalCode='', gender='', religion='', verification='', verification_material='', username=signIn_username, password=signIn_password, password_confirmation='', verification_id='', verification_method='')

     # Query user record from database
     user = Users.query.filter(Users.username == signIn_username).first()

     # Validate user credentials
     if user:
      # if the username and password is correct
      if bcrypt.checkpw(signIn_password.encode('utf-8'), user.password.encode('utf-8')):
       # User credentials are valid
       # Generate JWT token and store it in cookies
       # query the permissions list in the user table with the user id
       permissions= [permission.name for permission in user.permissions]
       token = jwt.encode({'id' : user.user_id, 'username': user.username, 'exp': datetime.utcnow() + timedelta(minutes=30), 'permissions': permissions}, login_app.config['SECRET_KEY'], algorithm='HS256')

       # Store the token in a cookie
       response = make_response(jsonify({'message': 'Login successful'}))
       response.set_cookie('token', value=token, expires=datetime.utcnow() + timedelta(minutes=30), httponly=True)

       # Redirect to the dashboard and some restricted resource
       return redirect(url_for('user_dashboard'))

      # if correct username but wrong password
      else:
       signin_errors['signIn_password'] = f"Password is invalid! Please enter again, if you forget your password, please click on the link below to reset your password!"
       raise ValueError

     # User credentials are invalid
     # Return error response or redirect to login page wit error message
     else:
      signin_errors['signIn_username'] = f"Sorry! We cannot find any user with this username and password! If you are a new user, click on the link below to register with us!"
      raise ValueError

    # handle the invalid form data
    except BaseException:
      return render_template('login.html', errors=signin_errors, validated_fields=validated_fields)

# create a resource for REST API to handle GET method with security check with user id and user's token
class DashBoardResource(Resource):
  def __init__(self) -> None:
   super().__init__()

  def render_dashboard(self, id):
    # run a query to find the username with the id and the token_id that is given
    user = Users.query.filter_by(user_id=id).first()
    return render_template('dashboard.html', name=user.username)

# add sign in resource to rest api
api.add_resource(SignInRenderResource, '/scholarsavings/login/')
api.add_resource(SignInResource, '/scholarsavings/validateuser/')
api.add_resource(DashBoardResource, '/scholarsavings/dashboard/')

# add login_routes to test the rest api

