## this is where all the REST APIs being put together and running on 1 application (server running)
# import libraries
from flask import Flask
from flask_restful import Api, Resource

# import the REST APIs
from register import db, RegistrationResource, registration_routes # -> REST API for registration
from login import SignInResource, verifyOTP # REST API for login and verifying OTP code
from user_profile import UserInformationResource # -> REST API for user to post their user's profile

# import database configurations
from get_env import database_type, database_username, database_password, database_host, database_port, database_name

app = Flask(__name__)
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
db.init_app(app)

# adding APIs to one resource
api = Api(app)
api.add_resource(RegistrationResource, '/studyhub/createaccount/')
api.add_resource(SignInResource, '/studyhub/validateuser/')
api.add_resource(verifyOTP, '/studyhub/verify-otp/<int:otp_code>/')
api.add_resource(UserInformationResource, '/studyhub/user-profile/user-information/')

app.register_blueprint(registration_routes)

if __name__ == '__main__':
 app.run(debug=True)
