# import neccessary libraries
import re
import pdb

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
def validate_users_input(errors, fname, lname, age, birthDay, gender, verification, verification_material, validate_verification_material) -> list:
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
  
  # identification validation
  # initialize a list of errors for verification
  verification_errors = {}

  if int(verification) == 1:
    errors['identification_id'] = f'Please choose one of the following method to verify your identification!'

  # users choose student email to verify
  elif int(verification) == 2:
    if not is_email(validate_verification_material):
     verification_errors['verification_material'] = f'Please enter an appropriate email (name@example.com)'
    #  raise ValueError('Please enter an appropriate email (name@example.com)')
    
  # users choose to upload an image or file
  else:  
    # check if any file is uploaded 
    if validate_verification_material.filename == '':
      verification_errors['verification_material'] = f'No selected file!'
      # raise ValueError('No selected file!')
    if not validate_files_upload(validate_verification_material):
      verification_errors['verification_material'] = f'Invalid file. Allowed file types are .png, .jpg, .jpeg, .pdf!'
      # raise ValueError('Invalid file. Allowed file types are .png, .jpg, .jpeg, .pdf!')
    if not validate_files_size(validate_verification_material):
      verification_errors['verification_material'] = f'File is too large! Please try again! The maximum size allowed is 10MB!'
      # raise ValueError('File is too large! Please try again! The maximum size allowed is 10MB!')

  return verification_errors
