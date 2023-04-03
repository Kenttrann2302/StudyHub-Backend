# import neccessary libraries
import re
import pdb
from flask import request
from werkzeug.utils import secure_filename
import zlib
import base64
import pdb
import os

# declare a path to save folders
UPLOAD_FOLDER = 'Files_upload/'

# function to validate if the string input is an email address
def is_email(email):
 # Define the regular expression pattern for email addresses
 pattern = r'^\w+[\w\.]*\@\w+\.[a-z]{2,3}$'
 # Use the match() method of the re module to check if the email matches the pattern
 match = re.match(pattern, email)
 
 # Return True if the email matches the pattern, otherwise False
 if match:
     return True
 else:
     return False

# allowed files upload
allowed_extensions = ['png', 'jpeg', 'jpg', 'pdf']

# allowed files size
max_content_length = 10*1024*1024 # maximum of 10MB is allowed 

# function to validate if the files are allowed
def validate_files_upload(file) -> bool:
 # get the extensions of the files uploaded
 return '.' in file.filename and \
  file.filename.rsplit('.', 1)[1].lower() in allowed_extensions

# function to validate the size of the files
def validate_files_size(file) -> bool:
 # return true if file has the size smaller than the allowed size
 if (file.content_length < max_content_length):
  return True
 else:
  return False

# function to validate all the fields of the users input
def validate_users_information(errors, fname, lname, age, birthDay, gender, profile_picture) -> list:
  # check if the users input the username and password
  if not fname or not lname:
    errors[fname] = f"Please enter your first name!"
    errors[lname] = f"Please enter your last name!"

  # check if the users input the correct age (must be at least 18) and birthday is associated with the age
  if not age or not birthDay:
    errors['age'] = f'Please enter your age!'
    errors['birthday'] = f'Please enter your birthday!'
  elif int(age) < 18:
    errors['age'] = f'Sorry! You must be at least 18 to register for this service!!!'
    errors['birthday'] = f'Sorry! You must be at least 18 to register for this service!!!'
  
  # gender validation
  if int(gender) == 1:
    errors['gender_id'] = f'Please select your gender!'
  
  # validate user's profile picture
  if profile_picture is not None:
    if not validate_files_upload(profile_picture):
      errors['profile-image'] = f'Invalid file. Allowed file types are .png, .jpg, .jpeg, .pdf!'
    if not validate_files_size(profile_picture):
      errors['profile-image'] = f'File is too large! Please try again! The maximum size allowed is 10MB!'

# This is a helper function that handle upload files and save them to the folder
def save_image(file):
  filename = secure_filename(file.filename)
  file_path = os.path.join(UPLOAD_FOLDER, filename)
  file.save(file_path)
  return file_path

# This is a helper function that handle the upload image for the user's profile picture
def get_profile_image():
  # convert the image upload to bytes code
  profile_image = request.files['profile_file'].read()
  # get the original image to validate the file
  validate_profile_upload = request.files['profile_file']
  # save the user's profile picture as a path to the userdatabase 
  profile_image = save_image(validate_profile_upload)
  return profile_image, validate_profile_upload

# This is a helper function to indicate if the user upload a file or a string email
def get_verification_material(verification_id):
 # if the users choose an email to verify
 if int(verification_id) == 2:
  verification_material = request.form['id_number']
  validate_verification_material = request.form['id_number']
  
 else:
  # convert the images uploaded to bytes code
  verification_material = request.files['verification_file'].read()
  # get the original image to validate the files
  validate_verification_material = request.files['verification_file']
  # save the user's files upload and send a path to the files to the database
  verification_material = save_image(validate_verification_material)
 return verification_material, validate_verification_material

# This is a helper function that initialize the validated_fields dictionary and then overwrite each kwargs while the users input the validated fields -> no need for users to re-enter the validated_fields
def create_validated_fields_dict(validated_fields, *args, **kwargs):
 for i, arg in enumerate(args):
  if i >= len(validated_fields):
   break
  validated_fields[list(validated_fields.keys())[i]] = arg
 
 # overwrite the value associated with each key in the dictionary
 for key, value in kwargs.items():
  if key in validated_fields:
   validated_fields[key] = value