########## SIGN UP PAGE #########
# import libraries 
from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import psycopg2
import pdb
from datetime import datetime

# import other files
from API.locationAPI import checkAddress
from database.models import db, Gender, Identification, Users

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# connect flask to postgres database using SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'

# Create the SQLAlchemy database object
db.init_app(app)

# create table if they don't exist
with app.app_context():
  inspector = inspect(db.engine)
  if not inspector.has_table('gender') and not inspector.has_table('identification') and not inspector.has_table('users'):
    db.create_all()
    # Check if the constraint already exists on the 'users' table
    constraints = inspector.get_check_constraints('users')
    for constraint in constraints:
      if constraint['name'] == 'age_check':
        print(f"The 'age_check' constraint already exits on the 'users' table")
        break
      else: 
        # Add the constraint if it does not already exist
        db.engine.execute('ALTER TABLE users ADD CONSTRAINT age_check CHECK(age >=18)')
        db.engine.execute('ALTER TABLE users ADD CONSTRAINT age_check CHECK (age = extract(year from age(date_of_birth)))')
        print(f"Added the 'age_check' constraint to the 'users' table.")
    print(f"Tables created successfully!")

class signUpForm:
  def __init__(self) -> None:
    pass

  # insert rows into the gender model
  def insert_gender_table(self) -> None:
    with app.app_context():
      # create a list of new gender instance
      new_genders = [
        Gender(id=1, gender_options='--select--'),
        Gender(id=2, gender_options='MALE'),
        Gender(id=3, gender_options='FEMALE'),
        Gender(id=4, gender_options='OTHERS'),
        Gender(id=5, gender_options='PREFER NOT TO TELL')
      ]

      # add the new gender to the session
      for gender in new_genders:
        try:
          db.session.add(gender)
          # commit the changes to the database
          db.session.commit()
          print(f"Gender {gender.gender_options} added successfully!")
        except:
          db.session.rollback()
          print(f"Gender {gender.gender_options} already exists!")

  # insert rows into the identification model
  def insert_identification_table(self) -> None:
    with app.app_context():
      # create a list of new identifications instance
      new_identifications = [
        Identification(id=1, identification_options='--select--'),
        Identification(id=2, identification_options='STUDENT EMAIL ADDRESS'),
        Identification(id=3, identification_options='STUDENT ID CARD'),
        Identification(id=4, identification_options='ENROLLMENT VERIFICATION LETTER'),
        Identification(id=5, identification_options='TRANSCRIPT')
      ]

      # add new identification to the session
      for identification in new_identifications:
        try:
          db.session.add(identification)
          # commit the changes to the database
          db.session.commit()
          print(f"Identification {identification.identification_options} added successfully!")
        except:
          db.session.rollback()
          print(f"Identification {identification.identification_options} already exists!")
  
  # render the signup page -> front-end
  def render_signup(self) -> None:
    with app.app_context():
      # query all of the gender options from the gender table 
      genders = Gender.query.all()

      # query all the identification options from the identification table
      identifications = Identification.query.all()

      return render_template('signup.html', gender_options = genders, identification_options = identifications)

  # perform action on the createaccount url 
  def createAccount(self):
    with app.app_context(): 
      # get the request method
      if request.method == 'POST':
        # get the users inputs
        try:
          firstName = request.form['fname']
          lastName = request.form['lname']
          midName = request.form['mname']
          age = request.form['age']
          birthDay = request.form['birthday']
          firstAddress = request.form['address1']
          secondAddress = request.form['address2']
          city = request.form['city']
          province = request.form['province']
          country = request.form['country']
          postalCode = request.form['postal_code']
          gender = request.form['gender_id']
          religion = request.form['religion']
          identification = request.form['identification_id']
          identification_number = request.form['id_number']
          # Initialize the errors dictionary:
          errors = {}

          # Validate the form data, if not -> send the error messages to the front-end
          # first name and last name validation
          if not firstName or not lastName:
            errors['fname'] = f'Please enter your first name!'
            errors['lname'] = f'Please enter your last name!'

          # age and birthday validation
          if not age or not birthDay:
            errors['age'] = f'Please enter your age!'
            errors['birthday'] = f'Please enter your birthday!'
          elif int(age) < 18:
            errors['age'] = f'Sorry! You must be at least 18 to register for this service!!!'
            errors['birthday'] = f'Sorry! You must be at least 18 to register for this service!!!'
          
          # gender validation
          if int(gender) == 1:
            errors['gender_id'] = f'Please select your gender!'
          
          # identification validation
          if int(identification) == 1:
            errors['identification_id'] = f'Please choose one of the following method to verify your identification!'

          elif int(identification) == 2:
            if len(identification_number) < 9:
              errors['id_number'] = f'Please enter a valid 9 digits of your passport number!'
          else:
            if len(identification_number) < 5:
              errors['id_number'] = f'Please enter a valid 5 digits of your driver license number!'

          # create a list of new user instance
          new_users = [
            Users(first_name=firstName, middle_name=midName, last_name=lastName, age=age, date_of_birth=birthDay, address_line_1=firstAddress, address_line_2=secondAddress, city=city, province=province, country=country, postal_code=postalCode, gender_id=gender, religion=religion, identification_id=identification, identification_number=identification_number)
          ]

          # if there is any invalid field is being caught
          if errors:
            pass
          
          # after getting the address, check for the validation using Googl Maps Geocoding API before execute the insert the element
          # if the address is not valid 
          addressChecking = checkAddress(firstAddress, city, province, country, postalCode, secondAddress)
          if not addressChecking.is_valid_address():
            # If the address is invalid or the response came back false
            pass
            
          # if all the fields are valid
          else:
            # add new user into users model
            for user in new_users:
              try:
                db.session.add(user)
                # commit the change to the database
                db.session.commit()
                print(f"User {user.first_name} {user.last_name} added successful!")
              except:
                db.session.rollback()
                print(f"User {user.first_name} {user.last_name} already exists!")

          result = Users.query.filter_by(name=firstName).first()

          if result:
            print(f"Data has been inserted successfully")
            return render_template("successful.html")
          else:
            print(f"Error inserting data")
            pass
        
        # catch the error if the address is invalid
        except ValueError:
          # Handle the case when the address is invalid
          # Render the form again and show an error message
          # get all of the gender options
          errors['address1'] = f'Please enter a valid address!'

          db.session.rollback()
          genders = Gender.query.all()
        
          identifications = Identification.query.all()

          return render_template('signup.html', error_message=errors, gender_options = genders, identification_options = identifications)
        
      
          
