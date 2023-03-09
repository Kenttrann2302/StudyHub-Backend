# these are helper functions that help validate the register form to make sure the users input fields all met the requirements
from flask import Flask
from hashlib import sha256
from datetime import datetime, timedelta

# This is a helper function to validate the registration form
# new_user = [username, password, email, phone_number]
def validate_registration_form(new_user, validate_new_user) -> list:
 for i, data in enumerate(new_user):
  case = {
   0: lambda: checkusername(data),
   1: lambda: checkpassword(data),
   2: lambda: check_email(data),
   3: lambda: check_phone_number(data),
  }
  case[i]()

 return validate_new_user

# function check the username input to see if the username is valid to the constraints from the database
def checkusername(username, errors, validate_new_user) -> None:
 if len(username) == 0:
  errors['username'] = f"Please enter your username!"

 elif len(username) < 8:
  errors['username'] = f"The length of the username must be longer than 8 characters!"

 else:
  validate_new_user.append(username)

# function check the password input to see if the password is valid to the constraints from the database
def checkpassword(username, password, errors, validate_new_user) -> None:
 length = len(password)
 if any(char.isdigit() for char in password): has_digit = True
 if any(char.isalpha() for char in password): has_alpha = True
 if any(char.isupper() for char in password): has_upper_char = True
 if any(char.islower() for char in password): has_lower_char = True
 if any(char in '!@#$%^&*():,.?/<>[]' for char in password): has_special_char = True
 if password != username: diff_username = True
 
 # switch through each case to handle the errors
 switch = {
  length < 8: f"The length of the password must be longer than 8 characters!",
  not has_digit: f"Password must contain at least 1 number!",
  not has_alpha: f"Password must contain at least 1 character!",
  not has_upper_char: f"Password must contain at least 1 uppercase letter!",
  not has_lower_char: f"Password must contain at least 1 lowercase letter!",
  not has_special_char: f"Password must contain at least 1 special character: !@#$%^&*():,.?/<>[]",
  not diff_username: f"Password must be different from the username!"
 }

 error_message = switch.get(True, None)
 if error_message is not None:
  errors['password'] = error_message
 else:
  validate_new_user.append(password)

# function check the email input to see if the email is valid to the constraints database
def check_email(email, errors, validated_new_user) -> None:
 split_email = email.split('@')
 switch = {
  len(split_email) != 2: f"Email address must contain a single '@' symbol!",
  len(split_email[0]): f"Email address must contain a username before the '@' symbol!",
  '.' not in split_email[1]: f"Email must contain a domain name with a '.' symbol!",
  len(split_email[1].split('.')[0]) == 0: f"Email address must contain a domain name before the '.' symbol."
 }
 
 error_message = switch.get(True, None)
 if error_message is not None:
  errors['email'] = error_message
 else:
  validated_new_user.append(email)

# function check the phone number input to see if the phone number is valid to the constraints of the database
def check_phone_number(phone_number, errors, validated_new_user):
 if len(phone_number) != 10:
  errors['phone_number'] = f"Phone number must be 10 digits long!"
 elif not phone_number.isdigit():
  errors['phone_number'] = f"Phone number must contain only digits!"
 else:
  validated_new_user.append(phone_number)

  
