########## SIGN UP PAGE FOR USERS INPUT FOR MACHINE LEARNING ALGORITHM FOR SAVING STRATEGIES #########
# import libraries 
from flask import Flask, redirect, url_for, render_template, jsonify, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, inputs
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
import psycopg2
import pdb
from datetime import datetime
import os

# import other files
from API.locationAPI import checkAddress
from database.users_models import db, UserInformation
from helper_functions.validate_users_information import validate_users_information, create_validated_fields_dict

user_profile_app = Flask(__name__)
user_profile_app.config['SERVER_NAME'] = 'localhost:5000'
user_profile_app.config['APPLICATION_ROOT'] = '/'
user_profile_app.config['PREFERRED_URL_SCHEME'] = 'http'
user_profile_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
api = Api(user_profile_app)
migrate = Migrate(user_profile_app, db)

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

# change the size for accepting files in the requests
user_profile_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 megabytes

# connect flask to postgres database using SQLALCHEMY
user_profile_app.config['SQLALCHEMY_DATABASE_URI'] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
engine = create_engine(f'{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}')
inspector = Inspector.from_engine(engine)

# Create the SQLAlchemy database object
db.init_app(user_profile_app)


# Querying and inserting into user profile database Flask_Restful API 
class UserInformationResource(Resource):
  def __init__(self) -> None:
    super().__init__()
  
  # querying the database to get the gender options
  def render_user_information(self) -> None:
    with user_profile_app.app_context():
      # query all of the gender options from the gender table 
      genders = Gender.query.all()

      # call the helper function to get the validated fields with empty strings for each field
      # validated_fields = create_validated_fields_dict(firstName='', midName='', lastName='', age='', birthDay='', firstAddress='', secondAdress='', city='', province='', country='', postalCode='', gender='', religion='', profile_picture='', user_bio='', user_interest='')

      # return render_template('user_profile.html', validated_fields = validated_fields, gender_options = genders)
      return jsonify({
        'message' : f'Ok',
        'gender_options' : genders
      }), 200

  # handle the POST request from the form data from user_profile.html
  def post(self, user_id, username):
    with user_profile_app.app_context(): 
      # get the request method
      if request.method == 'POST':
        # get the users inputs
        try:
          # get the user's input from the form data
          formData = reqparse.RequestParser()
          formData.add_argument("firstName", type=str, help="First name is required", required=True)
          formData.add_argument("midName", type=str, required=False)
          formData.add_argument("lastName", type=str, help="Last name is required", required=True)
          formData.add_argument("age", type=int, help="Age is required and must be larger than 18", required=True)
          formData.add_argument("birthDay", type=inputs.date, help="Birthday is required and the format must be YYYY-MM-DD", required=True)
          formData.add_argument("firstAddress", type=str, help="First address is required", required=True)
          formData.add_argument("secondAddress", type=str, help="Second address is required", required=True)
          formData.add_argument("city", type=str, help="City is required", required=True)
          formData.add_argument("province", type=str, help="Province is required", required=True)
          formData.add_argument("country", type=str, help="Country is required", required=True)
          formData.add_argument("postalCode", type=str, help="Postal Code is required and maximum of 10 characters long", required=True)
          formData.add_argument("gender", type=str, help="Gender is required", required=True)
          formData.add_argument("profile_image", type=str, help="This will be an image in bytes", required=False)
          formData.add_argument("religion", type=str, required=False)
          formData.add_argument("user_bio", type=str, required=False)
          formData.add_argument("user_interest", type=str, required=False)

          args = formData.parse_args()
          firstName = args['firstName']
          midName = args['midName']
          lastName = args['lastName']
          age = args['age']
          birthDay = args['birthDay']
          firstAddress = args['firstAddress']
          secondAddress = args['secondAddress']
          city = args['city']
          province = args['province']
          country = args['country']
          postalCode = args['postalCode']
          gender = args['gender']
          religion = args['religion']
          user_bio = args['user_bio']
          user_interest = args['user_interest']
          profile_image = args['profile_image']
          
          # Initialize the errors dictionary:
          errors = {}

          # Validate the form data, if not -> send the error messages to the front-end
          # validate the users input before insert the data into the database
          validated_errors = validate_users_information(errors, firstName, lastName, age, birthDay, gender, profile_image)

          # create a dictionary to store the validated fields by calling the helper function
          validated_fields = create_validated_fields_dict(firstName=firstName, midName=midName, lastName=lastName, age=age, birthDay=birthDay, firstAddress=firstAddress, secondAddress=secondAddress, city=city, province=province, country=country, postalCode=postalCode, gender=gender, religion=religion, user_bio=user_bio, user_interest=user_interest)

          # after getting the address, check for the validation using Google Maps Geocoding API before execute the insert the element
          # if the address is not valid 
          addressChecking = checkAddress(errors, firstAddress, city, province, country, postalCode, secondAddress)

          # if all the fields are valid
          if not errors and not validated_errors and addressChecking.is_valid_address():
            # query the database to check if there is any user that already exists with the same information
            result = UserInformation.query.filter_by(id=user_id, first_name=firstName, middle_name=midName, last_name=lastName, age=age, date_of_birth=birthDay, address_line_1=firstAddress, address_line_2=secondAddress, city=city, province=province, country=country, postal_code=postalCode, gender_id=gender, religion=religion, profile_image=profile_image).first()

            # check if user info already exists in the database then update the user's information based on the user id from the token
            if result:
              # try update the user's information in the database
              try:
                print(f'Found user {user_id} in the database! Now update the users information.')
                # create a list of columns need to be update
                columns = [result.first_name, result.middle_name, result.last_name, result.age, result.date_of_birth, result.address_line_1, result.address_line_2, result.city, result.province, result.country, result.postal_code, result.gender_id, result.religion, result.profile_image]

                # create a list of new row
                row = [firstName, midName, lastName, age, birthDay, firstAddress, secondAddress, city, province, country, postalCode, gender, religion, profile_image]

                j = 0
                # update the user's information
                for i in range(len(columns)):
                  columns[i] = row[j]
                  j += 1

                # when the data have been updated successfully
                db.session.commit()
                return jsonify({
                  'message' : f'Profile for user {username} has been updated successfully!'
                  }), 201
              
              # catch the server error and return an internal server error code
              except Exception as e:
                print(f'There is an error while updating the user information!')
                return jsonify({
                  'message' : f'User {username} profile cannot be updated due to an internal server error: {e}!'
                }), 500

            try: 
              # if the users information didn't exist in the database yet
              # create a list of new user instance
              new_user = UserInformation(first_name=firstName, middle_name=midName, last_name=lastName, age=age, date_of_birth=birthDay, address_line_1=firstAddress, address_line_2=secondAddress, city=city, province=province, country=country, postal_code=postalCode, gender_id=gender, religion=religion, profile_picture=profile_image, user_bio=user_bio, interests=user_interest)


              # add new user into users model
              db.session.add(new_user)
              # commit the change to the database -> 201 if successful
              db.session.commit()
              return jsonify({
                'message' : f'User {username} is added successfully!'
              }), 201

            # if there is an error with the server (Internal server error) -> 500
            except Exception as e:
              db.session.rollback()
              return jsonify({
                'message' : f'User {username} cannot be added with error: {e}!'
              }), 500

          # if there is any invalid field is being caught (including address, profile image(if any)), send the error to the front-end
          else:
            db.session.rollback()
            genders = Gender.query.all()
            # return render_template('user_information.html', error_message=errors, validated_fields = validated_fields, validated_errors = validated_errors, gender_options = genders)
            return jsonify({
              'message' : f'Client fields are invalid',
              'error_message' : errors,
              'validated_fields' : validated_fields,
              'validated_errors' : validated_errors,
              'gender_options' : genders
            }), 400

        # catch the error if there is an internal server error
        except Exception as e:
          db.session.rollback()
          genders = Gender.query.all()
          # return render_template('user_information.html', error_message=errors, validated_fields=validated_fields, validated_errors = validated_errors, gender_options = genders)
          return jsonify({
            'message' : f'User {username} cannot be added due to the internal server error: {e}',
            'error_message' : errors,
            'validated_fields' : validated_fields,
            'validated_errors' : validated_errors,
            'gender_option' : genders
          }), 500

api.add_resource(UserInformationResource, '/studyhub/user-profile/user-information/')   

if __name__ == "__main__":
  user_profile_app.run(debug=True)