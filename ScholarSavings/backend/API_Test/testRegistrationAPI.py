# Test the restful API that handle get request and post request into 2 different endpoints in registration.py
# import libraries
import unittest
from register import app, db, VerificationMethodsResource, RegistrationResource
from database.users_models import Verification, Registration
from flask import url_for

# create a class that test the API handles GET and POST request towards the database to insert and retrieve the data from the Verification table
class TestVerificationMethodsResource(unittest.TestCase):

 # set up the test configurations to create a Flask test client and a test database
 def setUp(self) -> None:
  app.config['SERVER_NAME'] = 'localhost:5000'
  app.config['APPLICATION_ROOT'] = '/'
  app.config['PREFERRED_URL_SCHEME'] = 'http'
  app.config['TESTING'] = True
  app.config['WTF_CSRF_ENABLED'] = False
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  self.app = app.test_client()
  db.create_all()
  self.resource = VerificationMethodsResource()

 # set up a tearDown method to clean up the database after each test
 def tearDown(self) -> None:
  db.session.remove()
  db.drop_all()

 # write a test to test the GET request to retrieve data from the verification table in the database
 def test_get_verification_options(self):
  # Insert verification methods into the database
  self.resource.insert_verification_table()

  # Simulate a GET request to the /scholarsavings/register/ endpoint
  response = self.app.get('/scholarsavings/register/')

  # Assert that the response status code is 200
  self.assertEqual(response.status_code, 200)

  # Assert that the response contains the expected verification options
  expected_options = ['--select--', 'Email', 'Phone Number']
  actual_options = [v['verification_options'] for v in response.json['verification_options']]
  self.assertEqual(actual_options, expected_options)

 # write a test to test the POST request to insert the data into the verification table in the database
 def test_post_verification_options(self):
  # Insert verification methods into the database
  self.resource.insert_verification_table()

  # Simulate a sample POST request to the /scholarsavings/register/ endpoint
  data = {
   'firstName'
  }


 