################# SIGN UP PAGE #################
# Create all 3 models for 3 tables (gender, identification and users) in the userdatabase
# import libraries 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import CheckConstraint
from datetime import datetime
from sqlalchemy import inspect
import pdb


db = SQLAlchemy()

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
  created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

  def __repr__(self):
    return '<Identification %r>' % self.identification_options

# Define a registration table to store the user's id, username (email), password, phone_number (for more authentication)
class Registration(db.Model):
  __tablename__ = 'registration'

  user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  username = db.Column(db.String(500), nullable=False, unique=True)
  password = db.Column(db.String(500), nullable=False, unique=True)
  email = db.Column(db.String(500), nullable=False, unique=True)
  phone_number = db.Column(db.String(15), unique=True, index=True)
  account_verified = db.Column(db.Boolean, nullable=False, default=False)
  created_at = db.Column(db.DateTime, default = datetime.utcnow, nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
  saving_challenges_signup = db.Column(db.Boolean, nullable=False, default=False) # indicate whether the users have registered for saving challenges algorithm

  # adding arguments contraints for registration table
  __table_args__ = (
    CheckConstraint("(length(username) >= 8)", name='username_check'),
    CheckConstraint("(length(phone_number) = 10 AND phone_number ~ \'^\\d+$\')", name='phone_number_check'),
    CheckConstraint("(length(password) >= 8 AND password != username)", name='password_check'),
    CheckConstraint("password REGEXP '[A-Z]' AND password REGEXP '[/|@|#|\$|\%|\^|\&|\*]' AND password REGEXP '[0-9]'", name='password_complexity_check'),
  )

  def __repr__(self) -> str:
    return '<Users %r>' % self.username 

# Define a user table to store the user's data when they sign up for the saving challenges algorithm
class Users(db.Model):
  __tablename__ = 'users'
  
  signup_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  user_id = db.Column(db.Integer, nullable=False, unique=True) # from the registration database
  first_name = db.Column(db.String(100), nullable=False)
  middle_name = db.Column(db.String(100), nullable=True)
  last_name = db.Column(db.String(100), nullable=True)
  age = db.Column(db.Integer, nullable=False)
  date_of_birth = db.Column(db.Date, nullable=False)
  address_line_1 = db.Column(db.String(500), nullable=False)
  address_line_2 = db.Column(db.String(500), nullable=True)
  city = db.Column(db.String(50), nullable=False)
  province = db.Column(db.String(50), nullable=False)
  country = db.Column(db.String(50), nullable=False)
  postal_code = db.Column(db.String(10), nullable=False)
  gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'), nullable=False)
  gender = db.relationship('Gender', backref='users')
  religion = db.Column(db.String(100), nullable=True)
  identification_id = db.Column(db.Integer, db.ForeignKey('identification.id'), nullable=False)
  identification = db.relationship('Identification', backref='users')
  identification_material = db.Column(db.String(500), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

  # add age constraint
  # __table_args__ = (
  #   CheckConstraint('age >= 18', name='age_check'),
  #   CheckConstraint('age = extract(year from age(date_of_birth))', name='age_check'),
  # )

  def __repr__(self):
    return '<Users %r>' % self.first_name % self.last_name

# Add a foreign key constraint to the gender_id field in the User model
db.ForeignKeyConstraint(['gender_id'], ['gender_id'])

# Add a foreign key constraint to the identification_id field in the User model
db.ForeignKeyConstraint(['identification_id'], ['identification_id'])


  