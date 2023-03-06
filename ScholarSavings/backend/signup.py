########## SIGN UP PAGE FOR USERS INPUT FOR MACHINE LEARNING ALGORITHM FOR SAVING STRATEGIES #########
# import libraries 
from flask import Flask, redirect, url_for, render_template, jsonify, request, flash, abort
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
from helper_functions.validate_fields import create_validated_fields_dict, get_verification_material
from helper_functions.users_tables_create import create_users_tables

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# change the size for accepting files in the requests
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 megabytes

# connect flask to postgres database using SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
engine = create_engine('postgresql://kenttran@localhost:5432/userdatabase')
inspector = Inspector.from_engine(engine)

# Create the SQLAlchemy database object
db.init_app(app)

# create 3 tables: Gender, Identification and Users according to the class models in users_models
create_users_tables(app=app, inspector=inspector, db=db)

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

      # call the helper function to get the validated fields with empty strings for each field
      validated_fields = create_validated_fields_dict(firstName='', midName='', lastName='', age='', birthDay='', firstAddress='', secondAdress='', city='', province='', country='', postalCode='', gender='', religion='', verification='', verification_material='')

      return render_template('signup.html', validated_fields = validated_fields, gender_options = genders, identification_options = identifications)

  # handle the POST request from the form data from signup.html
  def savings_challenge_signup(self):
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
          # call the helper function to send the approriate requests to get either an email string or binary files
          verification_material, validate_verification_material = get_verification_material(verification_id=verification)
          # Initialize the errors dictionary:
          errors = {}

          # Validate the form data, if not -> send the error messages to the front-end
          # validate the users input before insert the data into the database
          validated_errors = validate_users_input(errors, firstName, lastName, age, birthDay, gender, verification, verification_material, validate_verification_material)

          # create a dictionary to store the validated fields by calling the helper function
          validated_fields = create_validated_fields_dict(firstName=firstName, midName=midName, lastName=lastName, age=age, birthDay=birthDay, firstAddress=firstAddress, secondAdress=secondAddress, city=city, province=province, country=country, postalCode=postalCode, gender=gender, religion=religion, verification=verification, verification_material=verification_material)

          # after getting the address, check for the validation using Google Maps Geocoding API before execute the insert the element
          # if the address is not valid 
          addressChecking = checkAddress(firstAddress, city, province, country, postalCode, secondAddress)

          # if all the fields are valid
          if not errors and not validated_errors and addressChecking.is_valid_address():
            # query the database to check if there is any user that already exists with the same information
            result = Users.query.filter_by(first_name=firstName, middle_name=midName, last_name=lastName, age=age, date_of_birth=birthDay, address_line_1=firstAddress, address_line_2=secondAddress, city=city, province=province, country=country, postal_code=postalCode, gender_id=gender, religion=religion, identification_id=verification, identification_material=verification_material).first()

            # check if there is a user with the same info already in the database
            if result:
              flash(f"This user already exists in our system! Please register with a different user!")
              db.session.rollback()
              genders = Gender.query.all()
              identifications = Identification.query.all()
              return render_template('signup.html', error_message=errors, validated_fields = validated_fields, validated_errors = validated_errors, gender_options = genders, identification_options = identifications)
            
            # if the users information didn't exist in the database yet
            # create a list of new user instance
            new_users = [
              Users(first_name=firstName, middle_name=midName, last_name=lastName, age=age, date_of_birth=birthDay, address_line_1=firstAddress, address_line_2=secondAddress, city=city, province=province, country=country, postal_code=postalCode, gender_id=gender, religion=religion, identification_id=verification, identification_material=verification_material)
            ] 

            # add new user into users model
            for user in new_users:
              try:
                pdb.set_trace()
                db.session.add(user)
                # commit the change to the database
                db.session.commit()
                flash(f"User {user.first_name} {user.last_name} added successful!")

                # query the database to check if the users already register for an account
                if result is not None and result.isRegister == False:
                  return render_template('sign_up_successful.html')

              except:
                db.session.rollback()
                flash(f"User {user.first_name} {user.last_name} cannot be added!")
                abort(406)

          # if there is any invalid field is being caught (including verification materials and address)
          else:
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
        
      
          
