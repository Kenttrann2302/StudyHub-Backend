"""
Commented this files out for now, we will add proper unit test later
"""
# # Test the restful API that handle get request and post request into 2 different endpoints in registration.py
# # import libraries
# import unittest
# from main_homepage import app, db
# from register import register_app, VerificationMethodsResource, RegistrationResource
# from database.users_models import Verification, Registration
# from flask import url_for
# from flask_bcrypt import Bcrypt
# import pdb

# bcrypt = Bcrypt(app)

# # create a class that test the API handles GET request towards the database to retrieve the data from the Verification table
# class TestVerificationMethodsResource(unittest.TestCase):
#  # set up the test configurations to create a Flask test client and a test database
#  def setUp(self) -> None:
#   with app.app_context():
#     app.config['SERVER_NAME'] = 'localhost:5000'
#     app.config['APPLICATION_ROOT'] = '/'
#     app.config['PREFERRED_URL_SCHEME'] = 'http'
#     app.config['TESTING'] = True
#     app.config['WTF_CSRF_ENABLED'] = False
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     self.app = app.test_client()
#     db.create_all()
#     self.verification_resource = VerificationMethodsResource()

# #  # set up a tearDown method to clean up the database after each test
# #  def tearDown(self) -> None:
# #   with app.app_context():
# #     db.session.remove()
# #     db.drop_all()

#  # write a test to test the GET request to retrieve data from the verification table in the database
#  def test_get_verification_options(self):
#   with app.app_context():
#     # Insert verification methods into the database
#     self.verification_resource.insert_verification_table()

#     # Simulate a GET request to the /scholarsavings/register/ endpoint
#     response = self.app.get('/scholarsavings/register/')

#     # Assert that the response status code is 200
#     self.assertEqual(response.status_code, 200)

#     # Assert that the response contains the expected verification options
#     expected_options = ['--select--', 'Email', 'Phone Number']
#     actual_options = [v['verification_options'] for v in response.json['verification_options']]
#     self.assertEqual(actual_options, expected_options)

# # create a class that test the rest API that handle the POST request at RegistrationResource to input the form data into the database
# class TestRegistrationResource(unittest.TestCase):
#   # set up the test configurations to create a Flask test client and a test database
#  def setUp(self) -> None:
#   with app.app_context():
#     app.config['SERVER_NAME'] = 'localhost:5000'
#     app.config['APPLICATION_ROOT'] = '/'
#     app.config['PREFERRED_URL_SCHEME'] = 'http'
#     app.config['TESTING'] = True
#     app.config['WTF_CSRF_ENABLED'] = False
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     self.app = app.test_client()
#     db.create_all()
#     self.registration_resource = RegistrationResource()
#     # define a list of test password
#     self.test_password = ['Helloworld230204$']
#     self.new_user_id = None

#  # tear down the exact row that added for the test in the database
#  def tearDown(self):
#   with app.app_context():
#     if self.new_user_id is not None:
#       # Remove the row from the database
#       user_to_delete = db.session.query(Registration).filter_by(user_id=self.new_user_id).first()
#       db.session.delete(user_to_delete)
#       db.session.commit()

#  # Case 1: Write a test to test whether the valid form request can be handle by the API
#  def test_valid_post_registration(self):
#   with app.app_context():
#     # Case 1: Simulate a valid form fields POST request to the scholarsavings/createaccount/ endpoint
#     data = {
#     'username' : 'helloworld230204',
#     'password' : self.test_password[0],
#     'password_confirmation' : self.test_password[0],
#     'verification_id' : '2',
#     'areacode_id' : '+1',
#     'verification_method' : 'helloworld230204@gmail.com',
#     'register_errors' : {}
#     }

#     response = self.app.post('/scholarsavings/createaccount/', data=data)

#     # Assert that the response status code is 200 (OK)
#     self.assertEqual(response.status_code, 200)

#     # Assert that the user information was inserted into the database
#     test_new_user = [
#       Registration(username=data['username'], password=bcrypt.generate_password_hash(data['password']).decode('utf-8'), verification_id=int(data['verification_id']), verification_method=data['verification_method'])
#     ]

#     for test_user in test_new_user:
#       db.session.add(test_user)
#       db.session.commit()

#     inserted_user_info = Registration.query.filter_by(username='helloworld230204').first()
#     # retrieve the id that add after the test
#     self.new_user_id = inserted_user_info.user_id
#     self.assertIsNotNone(inserted_user_info)
