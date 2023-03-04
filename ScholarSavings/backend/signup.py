########## SIGN UP PAGE #########
# import libraries 
from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
import psycopg2
import pdb
from datetime import datetime

# import other files
from API.locationAPI import checkAddress
from database.users_models import db, Gender, Identification, Users
from helper_functions.formValidations import validate_users_input

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# connect flask to postgres database using SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
engine = create_engine('postgresql://kenttran@localhost:5432/userdatabase')
inspector = Inspector.from_engine(engine)

# Create the SQLAlchemy database object
db.init_app(app)

# create table if they don't exist
def create_tables() -> None:
  with app.app_context():
    # get all the table in the database
    table_names = inspector.get_table_names()
    if 'gender' not in table_names or 'identification' not in table_names or not 'users' in table_names:
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

# create all the tables
create_tables()

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

      return render_template('signup.html', validated_fields = validated_fields, gender_options = genders, identification_options = identifications)

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
          verification = request.form['identification_id']
          verification_material = request.form['id_number']
          # Initialize the errors dictionary:
          errors = {}

          # Validate the form data, if not -> send the error messages to the front-end
          # validate the users input before insert the data into the database
          validated_errors = validate_users_input(errors, firstName, lastName, age, birthDay, gender, verification, verification_material)
          # create a dictionary to store the validated fields
          validated_fields = {
            'firstName' : firstName,
            'midName' : midName,
            'lastName' : lastName,
            'age' : age,
            'birthDay' : birthDay,
            'firstAddress' : firstAddress,
            'secondAddress' : secondAddress,
            'city' : city,
            'province' : province,
            'country' : country,
            'postalCode' : postalCode,
            'gender' : gender,
            'religion' : religion,
            'verification' : verification,
            'verification_material' : verification_material,
          }

          # after getting the address, check for the validation using Google Maps Geocoding API before execute the insert the element
          # if the address is not valid 
          addressChecking = checkAddress(firstAddress, city, province, country, postalCode, secondAddress)
          # pdb.set_trace()
          # if all the fields are valid
          if not errors and not validated_errors and addressChecking.is_valid_address():
            # encode the verification materials from string to binary
            new_verification_material = verification_material.encode('utf-8')
            # create a list of new user instance
            new_users = [
              Users(first_name=firstName, middle_name=midName, last_name=lastName, age=age, date_of_birth=birthDay, address_line_1=firstAddress, address_line_2=secondAddress, city=city, province=province, country=country, postal_code=postalCode, gender_id=gender, religion=religion, identification_id=verification, identification_material=new_verification_material)
            ] 

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

          # if there is any invalid field is being caught (including verification materials and address)
          else:
            pass

          # query the database to check if the data has been inserted successfully
          result = Users.query.filter_by(first_name=firstName).first()

          if result:
            print(f"Data has been inserted successfully")
            return render_template("successful.html")
          else:
            print(f"Error inserting data")
            db.session.rollback()
            genders = Gender.query.all()
            identifications = Identification.query.all()
            return render_template('signup.html', error_message=errors, validated_fields = validated_fields, validated_errors = validated_errors, gender_options = genders, identification_options = identifications)
            
        # catch the error if the address is invalid
        except ValueError:
          # Handle the case when the address is invalid
          # Render the form again and show an error message
          # get all of the gender options
          errors['address1'] = f'Please enter a valid address!'

          db.session.rollback()
          genders = Gender.query.all()
          identifications = Identification.query.all()
          return render_template('signup.html', error_message=errors, validated_fields=validated_fields, validated_errors = validated_errors, gender_options = genders, identification_options = identifications)
        
      
          
