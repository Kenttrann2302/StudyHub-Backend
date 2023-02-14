from flask import Flask, url_for, render_template, redirect, request, send_from_directory
from signup import signUpForm
import psycopg2
import pdb
import os

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# include some static files such as JS or CSS
@app.route('/static-js/<path:filename>')

def serve_static(filename):
  root_dir = os.path.dirname(os.getcwd())
  return send_from_directory(os.path.join(root_dir, 'backend/static-js'), filename)


# rendering the homepage
@app.route('/home/')
def mainHomePage():
  return render_template('main_homepage.html')

# get the signup form
# create an object to signup
signUP = signUpForm()

@app.route('/hcm/signup/')
def signup():
  
  # add the gender table
  signUP.add_gender_table()
  # add the identification table
  signUP.add_identification_table()
  # create a table to store the user data after signing up
  signUP.create_user_table()
  return signUP.render_signup()

# add the user data input into the database to create an account for the user
@app.route('/createaccount/', methods = ['POST'])
# perform action on the createaccount url 
def createAccount():
  return signUP.createAccount()
    

if __name__ == '__main__':
  app.run(debug=True)