from flask import request
from werkzeug.utils import secure_filename
import zlib
import base64
import pdb
import os

# declare a path to save folders
UPLOAD_FOLDER = 'Files_upload/'

# This is a helper function that handle upload files and save them to the folder
def save_image(file):
  filename = secure_filename(file.filename)
  file_path = os.path.join(UPLOAD_FOLDER, filename)
  file.save(file_path)
  return file_path

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
def create_validated_fields_dict(*args, **kwargs):
 # initialize all the a dictionary of validated fields for user inputs
 validated_fields = {
   'firstName' : '',
   'midName' : '',
   'lastName' : '',
   'age' : '',
   'birthDay' : '',
   'firstAddress' : '',
   'secondAddress' : '',
   'city' : '',
   'province' : '',
   'country' : '',
   'postalCode' : '',
   'gender' : '',
   'religion' : '',
   'verification' : '',
   'verification_material' : '',
 }

 for i, arg in enumerate(args):
  if i >= len(validated_fields):
   break
  validated_fields[list(validated_fields.keys())[i]] = arg
 
 # overwrite the value associated with each key in the dictionary
 for key, value in kwargs.items():
  if key in validated_fields:
   validated_fields[key] = value

 return validated_fields