# import libraries
from flask import Flask, url_for, render_template, redirect, request, send_from_directory
import pdb
import os
import jwt

# import files from directories
from register import VerificationMethodsResource, RegistrationResource
from login import SignInRenderResource, SignInResource, DashBoardResource, login_app
from search import searchItemsResource
# aws sns sdks for sending email and sms subscription and confirmation to user's email or phone number
from AWS.aws_sns_helper_function import Email_Confirmation, SMS_Confirmation
# middleware function to verify users permission
from helper_functions.middleware_functions import token_required

# load in the sensitive data from .env
from dotenv import load_dotenv
# Load the configuration data from the .env file
load_dotenv()

# get the database connection information
database_type = os.getenv("DB_TYPE")
database_host = os.getenv("DB_HOST")
database_username = os.getenv("DB_USER")
database_password = os.getenv("DB_PASS")
database_port = os.getenv("PORT")
database_name = os.getenv("DB_NAME")

aws_verify_otp = os.getenv('AWS_EMAIL_VERIFY_OTP')

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
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
@app.route('/studyhub/search/')
def search():
  # create an object for searching class
  search = searchItemsResource()
  return search.search_results()

################################## REGISTER FORM for users account ('/studyhub/register/) ##########################
registration_resource = RegistrationResource()
verification_methods_resource = VerificationMethodsResource()

# rendering the registration form (username, password, email and phone number)
@app.route('/studyhub/register/')
def registration():
  # insert into verification table
  verification_methods_resource.insert_verification_table()
  return verification_methods_resource.registration()

# call an api to handle the post request from the form
@app.route('/studyhub/createaccount/', methods = ['POST'])
def registerNewUser():
  return registration_resource.createAccount()

################################## EMAIL CONFIRMATION HANDLER URL #####################################
email_confirmation_model = Email_Confirmation()

# render the template after the user successfully confirm the email
@app.route('/studyhub/confirm-email/', methods=['GET'])
def confirm_email_handler():
  response_message = email_confirmation_model.confirm_email()
  return response_message

################################# SMS CONFIRMATION HANDLER URL ################################
sms_confirmation_model = SMS_Confirmation()

# render the template after the user successfully confirm the sms
@app.route('/studyhub/confirm-sms/', methods=['GET'])
def confirm_sms_handler():
  response_message = sms_confirmation_model.confirm_sms()
  return response_message

################################## LOG IN FORM for users to sign into their account, this is where authentication takes place #########################
signin_render_resource = SignInRenderResource()
signin_authentication = SignInResource()

# rendering the login form page, response from the GET request (username and password)
@app.route('/studyhub/login/', methods=['GET'])
def signin():
  return signin_render_resource.SignInRender()

# call an api to handle the post request from the login form to authenticate the user login action
@app.route('/studyhub/validateuser/', methods=['POST'])
def loginPage():
  return signin_authentication.login()

################################# SENDING OTP VERIFICATION ########################
# send the otp to the user's endpoint(whether an email or password)
@app.route('/studyhub/send-otp/sms/?/', methods=['POST', 'GET'])
@token_required('can_receive_otp')
def send_otp_code():
  # get the token from cookies
  token = request.cookies.get('token')
  decoded_token = jwt.decode(token, login_app.config['SECRET_KEY'], algorithms=['HS256'])
  verification_id = decoded_token['verification_id']
  verification_method = decoded_token['verification_endpoint']
  # using AWS Pinpoint to send the otp code to the endpoint
  send_otp_request = sendOTP(channel_id=verification_id, channel=verification_method, allowedAttempts=3, codeLength=6, brandName='StudyHub', source='Login', language='en-US')
  send_otp_response = send_otp_request.send_otp(validityPeriod=15)
  return send_otp_response

# handle the post request to validate the user's otp
@app.route('/studyhub/validate-otp/sms/?/', methods=['POST'])
@token_required('can_validate_otp')
def validate_otp_code():
  # get the token from cookies
  token = request.cookies.get('token')
  decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
  verification_id = decoded_token['verification_id']
  verification_method = decoded_token['verification_endpoint']
  # using AWS Pinpoint to validate the code 
  validate_otp_request = sendOTP(channel_id=verification_id, channel=verification_method, allowedAttempts=3, codeLength=6, brandName='StudyHub', source='Login', language='en-US')
  valdiate_otp_response = validate_otp_request.verify_otp()
  return valdiate_otp_response

############################## OTP VERIFICATION FOR EMAIL ADDRESS ################################
@app.route('/studyhub/otp_verification/<string:email_address>/', methods=['POST'])
def otp_verification(email_address):
  if request.method == 'POST':
    # get the form data for the otp verification from the user
    try:
      otp_code = request.form['otp_code']
      return redirect(aws_verify_otp + email_address + '&otp=' + otp_code)
    except Exception as e:
      return ({'message' : f'There is an error while verifying the otp_code with error: {e}'}), 5000
    
if __name__ == '__main__':
  app.run(debug=True)

################################## USER'S ACCOUNT DASHBOARD ##################################
dashboard_obj = DashBoardResource()

# render the dashboard for user after they are authenticated
@app.route('/studyhub/dashboard/')
@token_required('can_view_dashboard')
def user_dashboard():
  # decode the token and get the username
  token = request.cookies.get('token')
  user_id = jwt.decode(token, login_app.config['SECRET_KEY'], algorithms=['HS256'])['id']
  return dashboard_obj.render_dashboard(user_id)

