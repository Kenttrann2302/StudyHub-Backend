# import libraries
from flask import Flask, url_for, render_template, redirect, request, send_from_directory
import psycopg2
import pdb
import os

# import files from directories
from signup import signUpFormResource, SavingChallengesResource
from register import VerificationMethodsResource, RegistrationResource
from search import searchItemsResource

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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
