############### REGISTER PAGE FOR USERS TO CREATE THEIR USERNAME AND PASSWORD FOR THE APPLICATION
# import libraries
from flask import Flask, redirect, url_for, session, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

# import the users models from the models.py
from database.users_models import db, Registration

# import other files
from helper_functions.users_tables_create import create_registration_table

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# connect to the userdatabase where store the information of the users from the sign up form
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
engine = create_engine('postgresql://kenttran@localhost:5432/userdatabase')
inspector = Inspector.from_engine(engine)

# create the sqlalchemy database object 
db.init_app(app)

# create the registration table according to the registration model
create_registration_table(app=app, inspector=inspector, db=db)

class Registration:
 def __init__(self) -> None:
  pass

 # this is a function to render the register form for users to register for the app
 def registration(self) -> None:
  with app.app_context():
   return render_template("registration.html")
  
 # this is a function to handle the POST request from the registration form and insert the registration fields into the database
 def createAccount(self) -> None:
  with app.app_context():
   pass

