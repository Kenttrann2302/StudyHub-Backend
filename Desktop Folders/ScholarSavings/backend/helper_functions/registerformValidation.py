# these are helper functions that help validate the register form to make sure the users input fields all met the requirements
from flask import Flask
from hashlib import sha256
from datetime import datetime, timedelta

# This is a helper function to validate the registration form
# new_user = [username, password, password_confirmation, email, phone_number]
def validate_registration_form(new_user, errors, verification_id, areacode_id) -> list:
 # create an empty list for users fields that are already validated
 validated_new_user = []
 for i, data in enumerate(new_user):
  case = {
   0: lambda: checkusername(username=data, errors=errors, validate_new_user=validated_new_user),
   1: lambda: checkpassword(username=new_user[0], password=data, errors=errors, validate_new_user=validated_new_user),
   2: lambda: checkpasswordconfirm(confirmed_password=data, password=new_user[1], errors=errors, validate_new_user=validated_new_user),
   3: lambda: check_verification(verification_method=data, verification_id=verification_id, errors=errors, validate_new_user=validated_new_user, areaCodeID=areacode_id),
  }
  case[i]()

 return validated_new_user

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

# function check if the confirmed password is the same as password
def checkpasswordconfirm(confirmed_password, password, errors, validate_new_user) -> None:
  if len(confirmed_password) == 0:
    errors['password-confirmation'] = f"Please enter the confirmation of the password!"
  elif confirmed_password != password:
    errors['password-confirmation'] = f"Password confirmation must be the same as password!"
  else:
    validate_new_user.append(confirmed_password)

# function check the email input to see if the email is valid to the constraints database
def check_verification(verification_method, verification_id, errors, validate_new_user, areaCodeID) -> None:
 # Case 0: user don't choose any method for authentication
 if (int(verification_id) == 1):
  errors['verification_id'] = f"Please choose one of the following methods to confirm your account!"

 # Case 1: user choose first method for authentication -> email
 # fix email validation regular expression
 elif int(verification_id) == 2:
  split_email = verification_method.split('@')

  switch = {
    len(split_email) != 2: f"Email address must contain a single '@' symbol!",
    len(split_email[0]): f"Email address must contain a username before the '@' symbol!",
    '.' not in split_email[1]: f"Email must contain a domain name with a '.' symbol!",
    len(split_email[1].split('.')[0]) == 0: f"Email address must contain a domain name before the '.' symbol."
  }
  
  error_message = switch.get(True, None)
  if error_message is not None:
    errors['verification-input'] = error_message
  else:
    validate_new_user.append(verification_method)
  
 # Case 2: user choose second method for authentication -> phone number
 elif int(verification_id) == 3:
  if len(verification_method) != 10:
    errors['verification-input'] = f"Phone number must be 10 digits long!"
  elif not verification_method.isdigit():
    errors['verification-input'] = f"Phone number must contain only digits!"
  else:
    validate_new_user.append('(' + areaCodeID + ')' + ' ' + verification_method)



  
