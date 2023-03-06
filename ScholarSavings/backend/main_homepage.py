from flask import Flask, url_for, render_template, redirect, request, send_from_directory
from signup import signUpForm
from search import searchItems
import psycopg2
import pdb
import os

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

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
  search = searchItems()
  return search.search_results()

# get the signup form
# create an object to signup
################################## SIGN UP FORM (/hcm/signup/) ###################################
signUP = signUpForm()

@app.route('/scholarsavings/signup/')
def signup():
  # add the gender table
  signUP.insert_gender_table()
  # add the identification table
  signUP.insert_identification_table()
  return signUP.render_signup()

# add the user data input into the database to create an account for the user
################################## CREATE ACCOUNT FOR USERS AFTER SIGNING UP ###############################
@app.route('/scholarsavings/savingchallenges/', methods = ['POST'])
# perform action on the createaccount url 
def savingChallengesInput():
  return signUP.createAccount()
    
if __name__ == '__main__':
  app.run(debug=True)
