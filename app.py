## this is where all the REST APIs being put together and running on 1 application (server running)
# import libraries
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api, Resource

# import database configurations
from get_env import (database_host, database_name, database_password,
                     database_port, database_type, database_username)
from login import SignInResource  # REST API for login and verifying OTP code
from login import verifyOTP
# import the REST APIs
from register import (RegistrationResource, db,  # -> REST API for registration
                      registration_routes)
from user_profile import \
    UserInformationResource  # -> REST API for user to post their user's profile

app = Flask(__name__)
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 megabytes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
db.init_app(app)

migrate = Migrate(app, db)

# adding APIs to one resource
api = Api(app)
api.add_resource(RegistrationResource, '/studyhub/createaccount/')
api.add_resource(SignInResource, '/studyhub/validateuser/')
api.add_resource(verifyOTP, '/studyhub/verify-otp/<int:otp_code>/')
api.add_resource(UserInformationResource, '/studyhub/user-profile/user-information/')

app.register_blueprint(registration_routes)

if __name__ == '__main__':
 app.run(debug=True)
