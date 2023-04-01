# import libraries 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import CheckConstraint
from datetime import datetime
from sqlalchemy import inspect
import pdb
import pytz
import uuid
from sqlalchemy.dialects.postgresql import UUID

# create a db instance
db = SQLAlchemy()

################################## USER'S ACCOUNT REGISTRATION MODEL ##################################
# Define a verification methods model that have foreign key to join registration model
class Verification(db.Model):
  __tablename__ = 'verification_methods'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  verification_options = db.Column(db.String(100), unique=True, nullable=False) # new non-null column for 2 factors authentication
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self):
    return '<Verification %r>' % self.verification_options

# Define a registration table to store the user's id, username (email), password, phone_number (for more authentication)
class Users(db.Model):
  __tablename__ = 'users'

  user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=str(uuid.uuid4), unique=True, nullable=False) # using universal unique identifier for best security practice
  username = db.Column(db.String(500), nullable=False, unique=True)
  password = db.Column(db.String(500), nullable=False, unique=True)
  password_salt = db.Column(db.String(500), nullable=False, unique=True)
  verification_id = db.Column(db.Integer, db.ForeignKey('verification_methods.id'), nullable=False)
  verification = db.relationship('Verification', backref='registration', uselist=True)
  verification_method = db.Column(db.String(500), nullable=False, unique=True)
  aws_token = db.Column(db.String(10000), nullable=True, unique=True)
  account_verified = db.Column(db.Boolean, nullable=False, default=False)
  is_active = db.Column(db.Boolean, nullable=False, default=True) # deactivate the user's account when they violate the terms and condition or they lock their account
  profile = db.relationship('UserInformation', uselist=False, backref='users') # perform a 1 to 1 relationship with the user's profile
  education = db.relationship('Education', backref='users', uselist=False) # perform a 1 to 1 relationship with the user's education model
  permissions = db.relationship('Permission', backref='users', lazy=True)
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self) -> str:
    return '<Users %r>' % self.user_id % self.username

# Define a permission table to have one-to-many relationship to registration table
class Permission(db.Model):
  __tablename__ = 'permission'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  name = db.Column(db.String(1000), nullable=False)
  user_id = db.Column(db.String(10000), db.ForeignKey('users.user_id'), nullable=False)

# Add a foreign key constraint to the gender_id field in the User model
db.ForeignKeyConstraint(['gender_id'], ['gender_id'])

# Add a foreign key constraint to the identification_id field in the User model
db.ForeignKeyConstraint(['identification_id'], ['identification_id'])

# Add a foreign key constraint to the verification_id fields in the Registration model
db.ForeignKeyConstraint(['verification_id'], ['verification_id'])



################################### USER'S PROFILE MODEL ###################################
# Define a gender model for database table
class Gender(db.Model):
  __tablename__ = 'gender'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  gender_options = db.Column(db.String(50), unique=True, nullable=False) # new non-null column
  created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

  def __repr__(self):
    return '<Gender %r>' % self.gender_options


# Define an identification model for students to verify themselves for database table
class Identification(db.Model):
  __tablename__ = 'identification'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  identification_options = db.Column(db.String(100), unique=True, nullable=False) # new non-null column
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self):
    return '<Identification %r>' % self.identification_options

# Define a user table to store the user's data when they sign up for the saving challenges algorithm
class UsersInformation(db.Model):
  __tablename__ = 'users_information'
  
  id = db.Column(UUID(as_uuid=True), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
  user_id = db.Column(db.String(10000), db.ForeignKey('users.user_id'), nullable=False) # form a one-to-one relationship with the user's id in the users table (using foreign key contraint)
  first_name = db.Column(db.String(100), nullable=False)
  middle_name = db.Column(db.String(100), nullable=True)
  last_name = db.Column(db.String(100), nullable=False)
  age = db.Column(db.Integer, nullable=False)
  date_of_birth = db.Column(db.Date, nullable=False)
  address_line_1 = db.Column(db.String(500), nullable=False)
  address_line_2 = db.Column(db.String(500), nullable=True)
  city = db.Column(db.String(50), nullable=False)
  province = db.Column(db.String(50), nullable=False)
  country = db.Column(db.String(50), nullable=False)
  postal_code = db.Column(db.String(10), nullable=False) # Geolocation API will be used to validate the address
  timezone = db.Column(db.String(50), nullable=False) # this timezone will be retrieved by Google Timezone API
  gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'), nullable=False) # 1 to 1 relationship with gender table
  gender = db.relationship('Gender', backref='users_information')
  religion = db.Column(db.String(100), nullable=True)
  education = db.relationship('Education', backref='users_information', uselist=False)
  profile_picture = db.Column(db.String(500), nullable=True) # allow users to add the profile picture
  user_bio = db.Column(db.Text, nullable=True) # allow user to update their bio information
  interests = db.Column(db.Text, nullable=True) # allow user to update their interests
  activity_status = db.Column(db.String(20), default='offline')
  identification_id = db.Column(db.Integer, db.ForeignKey('identification.id'), nullable=False) # 1 to 1 relationship with identification table
  identification = db.relationship('Identification', backref='users_information') 
  identification_material = db.Column(db.String(500), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self):
    return '<Users %r>' % self.first_name % self.last_name

# Define an institutions table to store all the options for all the institutes that are available at StudyHub
class Institutions(db.Model):
  __tablename__ = 'institution'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
  university_options = db.Column(db.String(500), nullable=False, unique=True)
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self) -> str:
    return '<Institution %r' % self.university_options 

# Define an educational table to store the users education information
class Education(db.Model):
  __tablename__ = 'education'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
  profile_id = db.Column(db.String(10000), db.ForeignKey('users_information.id'), unique=True) # perform a one-to-one relationship with the users profile which can be used to join 2 tables together.
  institution_id = db.relationship('Institutions', backref=False)


