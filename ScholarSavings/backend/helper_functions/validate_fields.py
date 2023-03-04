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