#Restful API Testing for registration flow
'''
Some requirements for all of these tests to pass for registration
+ Endpoint : /studyhub/user-account/
+ All requests and purposes of each request and expected corresponding response for each request APIs:
- GET request: 
    + Purpose: get all user's information and one user information
    + Expected responses:
        * 200 - return all users found
        * 404 - if no users found (find one user)
        * 500 - if any internal server error crash
- POST request:
    + Purpose: handle POST request from the registration form and inserting the registration fields into the database
    + Expected responses:
        * 201 - If the new entry is successfully entered the database (query the database after Twilio email is sent and verified)
        * 409 - If the username, password and/or verification method has been used!
        * 400 - If there is a field that was parsed is not in expected format from the client
        * 500 - If there is any internal server error that happens
    + Twilio expected responses:
        * Endpoint - "/studyhub/confirm-email", methods = GET
        * 200 or 201 - If create account confirmation email is sent successfully!
        * 500 - If Twilio email cannot be sent -> expected appropriate behavior of the API
- PATCH request:
    + Purpose: handle updating the user information if the user forgot their username or password
    + Expected responses:
        * 201 - If the entry is found and updated correctly in the database (query the database after Twilio email is sent and verified)
        * 404 - If the user is not found in the database
        * 409 - If the user new username and/or password and/or verification method has been used
        * 403 - If the user's verification method for this account is not yet verified when registering.
        * 500 - If there is any internal server error that is happening during the response runtime
    + Twilio expected responses:
        * Endpoint: "/studyhub/confirm-password-change", method = GET
        * 200 or 201 - If the email confirmation to change the password is sent successfully!
        * 500 - If Twilio email cannot be sent -> expected approriate behavior of the API
- DELETE request:
    + Purpose: a delete method to delete an entry from the database
    + Expected responses:
        * Endpoint: "/studyhub/confirm-account-deletion", method = GET
        * 201 - If the entry is found and delete successfully (query the database after Twilio email is sent and verified).
        * 404 - If the entry is not found in the database
        * 403 - If the user's verification method for this account is not yet verified when registering.
        * 500 - If there is any internal server error that is happening during the response runtime
    + Twilio expected responses:
        * 200 or 201 - If the email confirmation to delete the resource is sent successfully!
        * 500 - If the Twilio email cannot be sent -> expected approriate behavior of the API
- Testing requests for register with third party services such as Google 
'''
# import libraries
import unittest
from app import app
from database.users_models import db
from register import RegistrationResource, registration_routes
from database.users_models import Users
from flask import url_for
from flask_bcrypt import Bcrypt
import pdb

# import from other files
from get_env import (
    database_host,
    database_name,
    database_password,
    database_port,
    database_type,
    database_username,
)

# unit test for registration flow REST API
class TestRegistrationResource(unittest.TestCase):
    def __init__(self, app) -> None:
        self.app = app
        self.db = db
    
    # set up the test configurations to create a Flask test client and a test database
    def setUp(self) -> None:
        self.app.config['APPLICATION_ROOT'] = '/'
        self.app.config['PREFERRED_URL_SCHEME'] = 'http'
        self.app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
        self.app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 megabytes
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()
        self.db.create_all()
        self.registration_resource = RegistrationResource()
            

    # tear down the exact row that added for the test in the database
    # def tearDown(self):
    #     if self.new_user_id is not None:
    #         # Remove the row from the database
    #         user_to_delete = db.session.query(Registration).filter_by(user_id=self.new_user_id).first()
    #         db.session.delete(user_to_delete)
    #         db.session.commit()

    # test GET request
    def test_get_all_users_not_found(self):
        # Test 1:  Should return 404 since no user in the database
        # send a GET request to the endpoint
        response = self.app.get("/studyhub/user-account/")

        # assert the response status code
        self.assertEqual(response.status_code, 404)
        self.assertIsNot(response.status_code, 200)

        expected_data = {}
        self.assertEqual(response.json, expected_data)
    
    def test_get_all_users_found(self):
        # Test 2: return all the users in the database -> 200
        # return default entries in the database
        expected_data = {
            'user_id' : '3baf5708-c331-4c91-bb83-bf33bb037663',
            'username' : 'kenttran2302',
            'password' : 'LukeFootBall1357&',
            'verification_method' : 'Email',
            'verification' : 'duykhang2302@gmail.com',
        } 
        # send a GET request to the endpoint
        response = self.app.get("studyhub/user-account")

        # assert the response status code
        self.assertEqual(response.status_code, 200)

        self.assertSetEqual(response.json, expected_data)
        

    '''
    # Case 1: Write a test to test whether the valid form request can be handle by the API
    def test_valid_post_registration(self):
        # Case 1: Simulate a valid form fields POST request to the scholarsavings/createaccount/ endpoint
        data = {
        'username' : 'helloworld230204',
        'password' : self.test_password[0],
        'password_confirmation' : self.test_password[0],
        'verification_id' : '2',
        'areacode_id' : '+1',
        'verification_method' : 'helloworld230204@gmail.com',
        'register_errors' : {}
        }

        response = self.app.post('/scholarsavings/createaccount/', data=data)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the user information was inserted into the database
        test_new_user = [
        Registration(username=data['username'], password=bcrypt.generate_password_hash(data['password']).decode('utf-8'), verification_id=int(data['verification_id']), verification_method=data['verification_method'])
        ]

        for test_user in test_new_user:
            db.session.add(test_user)
            db.session.commit()

            inserted_user_info = Registration.query.filter_by(username='helloworld230204').first()
            # retrieve the id that add after the test
            self.new_user_id = inserted_user_info.user_id
            self.assertIsNotNone(inserted_user_info) '''
