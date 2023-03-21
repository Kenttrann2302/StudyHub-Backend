# import libraries
from flask import Flask, url_for, render_template, redirect, request, send_from_directory
import psycopg2
import pdb
import os
import jwt

# import files from directories
from signup import signUpFormResource, SavingChallengesResource
from register import VerificationMethodsResource, RegistrationResource
from login import SignInRenderResource, SignInResource, DashBoardResource
from search import searchItemsResource
# import the users models from the models.py
from database.users_models import db, Users, Verification
# aws sns sdks for sending email and sms subscription and confirmation to user's email or phone number
from AWS.aws_sns_helper_function import Email_Confirmation, SMS_Confirmation
# middleware function to verify users permission
from helper_functions.middleware_functions import token_required

# load in the sensitive data from .env
if(os.environ.get("DB_TYPE") == None):
  from dotenv import load_dotenv
  from config.definitions import ROOT_DIR
  load_dotenv(os.path.join(ROOT_DIR, 'config', 'conf', '.env'))

# get the database connection information
database_type = os.environ.get("DB_TYPE")
database_host = os.environ.get("DB_HOST")
database_username = os.environ.get("DB_USER")
database_password = os.environ.get("DB_PASS")
database_port = os.environ.get("PORT")
database_name = os.environ.get("DB_NAME")

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = '{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}'
db.init_app(app)
# app.register_blueprint('registration_routes')

# include some static files for javascript
@app.route('/static-js/<path:filename>')

# adding the static files path towards the javascript files
def serve_static_js(filename):
  root_dir = os.path.dirname(os.getcwd())
  return send_from_directory(os.path.join(root_dir, 'backend/static-js'), filename)

# include some static files for css
@app.route('/static-css/<path:filename>')

# adding the static files path towards the css files
def serve_static_css(filename):
  root_dir = os.path.dirname(os.getcwd())
  return send_from_directory(os.path.join(root_dir, 'backend/static-css'), filename)

################################### HOMEPAGE (/home/) ######################################
# rendering the homepage
@app.route('/home/')
def mainHomePage():
  return render_template('main_homepage.html')

# implementing search engine with search endpoint
@app.route('/scholarsavings/search/')
def search():
  # create an object for searching class
  search = searchItemsResource()
  return search.search_results()

################################## REGISTER FORM for users account ('/scholarsavings/register/) ##########################
registration_resource = RegistrationResource()
verification_methods_resource = VerificationMethodsResource()

# rendering the registration form (username, password, email and phone number)
@app.route('/scholarsavings/register/')
def registration():
  # insert into verification table
  verification_methods_resource.insert_verification_table()
  return verification_methods_resource.registration()

# call an api to handle the post request from the form
@app.route('/scholarsavings/createaccount/', methods = ['POST'])
def registerNewUser():
  return registration_resource.createAccount()


################################## EMAIL CONFIRMATION HANDLER URL #####################################
email_confirmation_model = Email_Confirmation()

# render the template after the user successfully confirm the email
@app.route('/scholarsavings/confirm-email/', methods=['GET'])
def confirm_email_handler():
  response_message = email_confirmation_model.confirm_email()
  return response_message

################################# SMS CONFIRMATION HANDLER URL ################################
sms_confirmation_model = SMS_Confirmation()

# render the template after the user successfully confirm the sms
@app.route('/scholarsavings/confirm-sms/', methods=['GET'])
def confirm_sms_handler():
  response_message = sms_confirmation_model.confirm_sms()
  return response_message

################################## LOG IN FORM for users to sign into their account, this is where authentication takes place #########################
signin_render_resource = SignInRenderResource()
signin_authentication = SignInResource()

# rendering the login form page, response from the GET request (username and password)
@app.route('/scholarsavings/login/', methods=['GET'])
def signin():
  return signin_render_resource.SignInRender()

# call an api to handle the post request from the login form to authenticate the user login action
@app.route('/scholarsavings/validateuser/', methods=['POST'])
def loginPage():
  return signin_authentication.login()

################################## USER'S ACCOUNT DASHBOARD ##################################
dashboard_obj = DashBoardResource()
permission_list = ['can_view_dashboard', 'can_register_saving_challenges', 'can_use_geolocation_api']

# render the dashboard for user after they are authenticated
@app.route('/scholarsavings/dashboard/')
@token_required(permissions_list=permission_list)
def user_dashboard():
  # decode the token and get the username
  token = request.cookies.get['token']
  user_id = jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')['id']
  return dashboard_obj.render_dashboard(user_id)
  
################################## SIGN UP FORM for saving strategy algorithm ('/scholarsavings/signup/)###################################
signUP = signUpFormResource()
savingChallenges = SavingChallengesResource()

@app.route('/scholarsavings/treasurehunt/signup/')
def signup():
  # add the gender table
  signUP.insert_gender_table()
  # add the identification table
  signUP.insert_identification_table()
  return signUP.render_signup()

@app.route('/scholarsavings/treasurehunt/signup/process/', methods = ['POST'])
# perform action on the url for treasure hunting game 
def savingChallengesInput():
  return savingChallenges.savings_challenge_signup()
    
if __name__ == '__main__':
  app.run(debug=True)
