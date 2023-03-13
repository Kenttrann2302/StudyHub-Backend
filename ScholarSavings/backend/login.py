######################## LOG IN PAGE FOR USERS TO SIGN INTO THEIR ACCOUNT #############
# import libraries
from flask import Flask, redirect, url_for, session, render_template, request, abort, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash
from sqlalchemy import create_engine
import pdb

# import the users models from the models.py
from database.users_models import db, Registration, Verification
from helper_functions.signupformValidations import create_validated_fields_dict

# login app configuration
login_app = Flask(__name__)
login_app.config['SERVER_NAME'] = 'localhost:5000'
login_app.config['APPLICATION_ROOT'] = '/'
login_app.config['PREFERRED_URL_SCHEME'] = 'http'
login_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
login_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set up the login app for rest api
api = Api(login_app)

db.init_app(login_app)

# register the app instance with the endpoints we are using for this app
login_routes = Blueprint('login_routes', __name__)

# Add an API Test Configuration
login_app.config['TESTING'] = True
login_app.config['WTF_CSRF_ENABLED'] = False

migrate = Migrate(login_app, db)
bcrypt = Bcrypt(login_app)

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
     user = Registration.query.filter(Registration.username == signIn_username).first()

     # Validate user credentials
     if user:
      hashed_signin_password = bcrypt.generate_password_hash(signIn_password)
      # if the username and password is correct
      if check_password_hash(user.password, hashed_signin_password):
       # User credentials are valid
       # Generate JWT token and store in cookies
       # Redirect to the main page or some restricted resource
       return render_template('dashboard.html', name=signIn_username)

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

# add sign in resource to rest api
api.add_resource(SignInRenderResource, '/scholarsavings/login/')
api.add_resource(SignInResource, '/scholarsavings/validateuser/')

     


