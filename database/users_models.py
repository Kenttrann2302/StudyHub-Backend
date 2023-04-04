# Here are the models that store the users profiles information (most important)

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

  user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False) # using universal unique identifier for best security practice
  username = db.Column(db.String(500), nullable=False, unique=True)
  password = db.Column(db.String(500), nullable=False, unique=True)
  password_salt = db.Column(db.String(500), nullable=False, unique=True)
  verification_id = db.Column(db.Integer, db.ForeignKey('verification_methods.id'), nullable=False)
  verification = db.relationship('Verification', backref='registration', uselist=True)
  verification_method = db.Column(db.String(500), nullable=False, unique=True)
  aws_token = db.Column(db.String(500), nullable=True, unique=True)
  account_verified = db.Column(db.Boolean, nullable=False, default=False)
  is_active = db.Column(db.Boolean, nullable=False, default=True) # deactivate the user's account when they violate the terms and condition or they lock their account
  profile = db.relationship('UserInformation', uselist=False, backref='users') # perform a 1 to 1 relationship with the user's profile
  education = db.relationship('Education', backref='users', uselist=False) # perform a 1 to 1 relationship with the user's education model
  permissions = db.relationship('Permission', backref='users', lazy=True) # perform a 1 to many relationship with the user's permission model
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self) -> str:
    return '<Users %r>' % self.user_id % self.username

# Define a permission table to have one-to-many relationship to registration table
class Permission(db.Model):
  __tablename__ = 'permission'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
  name = db.Column(db.String(1000), nullable=False)
  user_id = db.Column(db.String(500), db.ForeignKey('users.user_id'), nullable=False)

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

# Define a user table to store the user's data when they sign up for the saving challenges algorithm
class UsersInformation(db.Model):
  __tablename__ = 'users_information'
  
  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
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
  religion = db.Column(db.String(100), nullable=True)
  profile_picture = db.Column(db.String(500), nullable=True) # allow users to add the profile picture
  user_bio = db.Column(db.Text, nullable=True) # allow user to update their bio information
  interests = db.Column(db.Text, nullable=True) # allow user to update their interests
  activity_status = db.Column(db.String(20), default='offline')
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  # relationship
  user_id = db.Column(db.String(500), db.ForeignKey('users.user_id'), nullable=False) # form a one-to-one relationship with the user's id in the users table (using foreign key contraint)

  gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'), nullable=False) # 1 to many relationship with gender table
  gender = db.relationship('Gender', backref='users_information')

  education = db.relationship('Education', backref='users_information', uselist=False)

  study_preferences = db.relationship('StudyPreferences', backref='users_information', uselist=False)

  availability = db.relationship('AvailabilitySchedule', backref='users_information', uselist=False)

  long_term_goal = db.relationship('LongTermGoal', backref='users_information', uselist=False)

  communication_preferences = db.relationship('CommunicationPreferences', backref='users_information', uselist=False)

  def __repr__(self):
    return '<Users %r>' % self.first_name % self.last_name



#################### EDUCATION IN USER'S PROFILE ##################
# Define an institutions table to store all the options for all the institutes that are available at StudyHub
class Institutions(db.Model):
  __tablename__ = 'institutions'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
  university_options = db.Column(db.String(200), nullable=False, unique=True)
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a degree models to store all the options for all the degrees that are available at studyhub
class Degree(db.Model):
  __tablename__ = 'degree'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
  degree_name = db.Column(db.String(100), nullable=False, unique=True) # example: "Bachelor of Computer Science"
  degree_description = db.Column(db.String(500), nullable=False, unique=True) # example: "A degree that focuses on the study of computers and computing technologies"
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a majors models to store all the options for the fields of study that are available at studyhub
class Major(db.Model):
  __tablename__ = 'majors'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
  majors_name = db.Column(db.String(100), nullable=False, unique=True) # example: "Computer Science, Math, Software Engineering"
  major_description = db.Column(db.String(500), nullable=False, unique=True) # example: "A field that is learning about how to apply math to real life application such as Data Analyst"
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define an identification model for students to verify themselves such as using student id card, proof of enrollment
class Identification(db.Model):
  __tablename__ = 'identification'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  identification_options = db.Column(db.String(100), unique=True, nullable=False) # new non-null column
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define an educational table to store the users education information
class Education(db.Model):
  __tablename__ = 'education'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
  profile_id = db.Column(db.String(500), db.ForeignKey('users_information.id'), unique=True) # perform a many-to-one relationship with the users profile, one user can have multiple education records.
  institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
  institution_name = db.relationship('Institutions', backref='education', uselist=True) # perform a 1 to many relationship with the institution model
  start_date = db.Column(db.Date, nullable=False)
  graduation_date = db.Column(db.Date, nullable=False)
  # user's proof of enrollment
  identification_id = db.Column(db.Integer, db.ForeignKey('identification.id'), nullable=False) # 1 to 1 relationship with identification table
  identification = db.relationship('Identification', backref='education') 
  identification_material = db.Column(db.String(500), nullable=False) # image of the identification
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  user_profile = db.relationship('UserInformation', backref=db.backref('education', lazy=True)) # many to one relationship with the user profile model

  def __repr__(self) -> str:
    return f'<Education {self.id}>'



############ STUDY PREFERENCES IN USER'S PROFILE ###########
# Define a study environment atmosphere model that contains all the options for the users to choose for the study environment atmosphere
class StudyEnvironment(db.Model):
  __tablename__ = 'study_environment'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  study_env_atm = db.Column(db.String(500), nullable=False) # example: quiet space, background noise,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a study environment location model that contains all the options about the locations for the users to choose for the study environment location
class StudyLocation(db.Model):
  __tablename__ = 'study_location'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  study_env_loc = db.Column(db.String(500), nullable=False) # example: library, home,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a study time frame model that contains all the options for the users to choose the time frame for their studies
class StudyTimeFrame(db.Model):
  __tablename__ = 'study_time'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  study_time_frame = db.Column(db.String(500), nullable=False) # example: early bird, night owl,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a study time session model that contains all the options for the users to choose the prefered duration for their studies
class StudyTimeSession(db.Model):
  __tablename__ = 'study_session'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  study_duration = db.Column(db.String(500), nullable=False) # example: short but frequent session, long but less session,..
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a study habits model that contains all the options for the users to choose all the study techniques
class StudyTechniques(db.Model):
  __tablename__ = 'study_techniques'

  id = db.Column(db.Integer, primary_key = True, autoincrement=True)
  study_techniques = db.Column(db.String(500), nullable=False) # example: read and take notes, flash cards,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a collaboration model that contains all the options for the users to choose the size of their study group
class Collaboration(db.Model):
  __tablename__ = 'collaboration'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  collaboration_styles = db.Column(db.String(500), nullable=False) # example: regular study groups, occassional meet-ups,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False) 

# Define a learning styles model that contains all the options for the users to pick their favorite learning style
class LearningStyles(db.Model):
  __tablename__ = 'learning_styles'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  learning_styles = db.Column(db.String(500), nullable=False) # example: visual aids, auditory aids,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a study methodology model that contains all the options for the users to choose
class StudyMethodology(db.Model):
  __tablename__ = 'study_methodology'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  study_methodology = db.Column(db.String(500), nullable=False) # example: set goals and track progress, focus on the process of learning than result,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a study material model that contains all the options for the users to choose
class StudyMaterialPreferences(db.Model):
  __tablename__ = 'study_materials'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  study_materials_preference = db.relationship(db.String(500), nullable=False) # example: online resources, digital textbooks, traditional print materials,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a study preferences model to store the user's study preference and habits
# This model will perform a one to one relationship with the users profile -> one user will have one study preference for the k-means clustering algorithm
class StudyPreferences(db.Model):
  __tablename__ = 'study_preferences'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

  user_id = db.Column(db.String(500), db.ForeignKey('users_information.id'), nullable=False) # form a one to one relationship with the user's profile

  # study environment preferences
  study_env_id = db.Column(db.Integer, db.ForeignKey('study_environment.id'), nullable=False)
  study_loc_id = db.Column(db.Integer, db.ForeignKey('study_location.id'), nullable=False)
  study_env_atm_pref = db.relationship('StudyEnvironment', backref='study_preferences', uselist=True)  
  study_loc_pref = db.relationship('StudyLocation', backref='study_preferences', uselist=True)

  # study time preferences
  study_time_frame_id = db.Column(db.Integer, db.ForeignKey('study_time.id'), nullable=False)
  study_session_id = db.Column(db.Integer, db.ForeignKey('study_session.id'), nullable=False)
  study_time_frame_pref = db.relationship('StudyTimeFrame', backref='study_time', uselist=True)
  study_session_pref = db.relationship('StudyTimeSession', backref='study_session', uselist=True)

  # study habits
  study_techniques_id = db.Column(db.Integer, db.ForeignKey('study_techniques.id'), nullable=False)
  study_techniques_options = db.relationship('StudyTechniques', backref='study_techniques', uselist=True)

  # collaboration
  collaboration_styles_id = db.Column(db.Integer, db.ForeignKey('collaboration.id'))
  collaboration_chosen = db.Column(db.Boolean, nullable=False) 
  collaboration_number = db.Column(db.Integer, nullable=False) # a group study from 1 to 10
  collaboration_types = db.relationship('Collaboration', backref='study_preferences', uselist=True) 

  # learning styles 
  learning_styles_id = db.Column(db.Integer, db.ForeignKey('learning_styles.id'), nullable=False)
  learning_styles = db.relationship('LearningStyles', backref='study_preferences', uselist=True)

  # motivation 
  study_motivation = db.Column(db.Text, nullable=False) # let the users input their own motivation

  # study methodology
  study_methodology_id = db.Column(db.Integer, db.ForeignKey('study_methodology.id'), nullable=False)
  study_methodology = db.relationship('StudyMethodology', backref='study_preferences', uselist=True)

  # study material
  study_material_id = db.Column(db.Integer, db.ForeignKey('study_materials.id'), nullable=False)
  study_material = db.relationship('StudyMaterialPreferences', backref='study_preferences', uselist=True)

  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self) -> str:
    return '<Study Preference %r>' % self.id


################################# AVAILABILITY (USER'S TIME SCHEDULE IN USER'S PROFILE) #################################
# Define a model stores the user's availability or time schedule for best matching result
class AvailabilitySchedule(db.Model):
  __tablename__ = 'availability_schedule'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
  user_id = db.Column(db.String(500), db.ForeignKey('users_information.id'), nullable=False)
  timezone = db.Column(db.Integer, db.ForeignKey('users_information.id'), nullable=False)
  schedule = db.Column(db.JSON, nullable=False) # a json object that stores the user's weekly schedule, with each day of the week represented as a key and list of time ranges as the value
  preferred_times = db.Column(db.JSON, nullable=False) # a json object that stores the user's preferred study times, with each time represented as a key and a boolean value indicating whether the user is avalable at that time
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self) -> str:
    return '<Availability Schedule %r' % self.id



########### LONG TERM GOAL (USER'S PROFILE) ###########
# Define a model that stores the user's long term goal
class LongTermGoal(db.Model):
  __tablename__ = 'long_term_goal'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
  user_id = db.Column(db.String(500), db.ForeignKey('users_information.id'), nullable=False)
  goal_name = db.Column(db.Text, nullable=False) # users will input their long term goal achievements
  goal_description = db.Column(db.Text, nullable=False) # users will describe their goal achievements such as what elements they need to achieve the goals
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self) -> str:
    return '<Long Term Goal %r' % self.id



########## COMMUNICATION PREFERENCES ##########
# Define a model that stores all the options for the communication methods that are supported in StudyHub
class CommunicationMethods(db.Model):
  __tablename__ = 'communication_methods'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
  communication_methods = db.Column(db.String(500), nullable=False) # example: Zoom, Microsoft Office, Slack, Instagram, SnapChat,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a model that stores all the options for the communication frequency that the users can choose
class CommunicationFrequency(db.Model):
  __tablename__ = 'communication_frequency'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
  communication_frequency = db.Column(db.String(500), nullable=False) # example: daily check-ins, weekly meetings, sporadic communication,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

# Define a model that stores all the options for the communication time of the dat that users can choose from
class CommunicationTime(db.Model):
  __tablename__ = 'communication_time'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
  communication_time = db.Column(db.String(500), nullable=False) # example: day, afternoon, night time,...
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)
  

# Define a model that stores the user's preferred communication methods
class CommunicationPreferences(db.Model):
  __tablename__ = 'communication_preferences'

  id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
  user_id = db.Column(db.String(500), db.ForeignKey('users_information.id'), nullable=False)
  communication_methods_id = db.Column(db.Integer, db.ForeignKey('communication_methods.id'), nullable=False)
  communication_methods = db.relationship('CommunicationMethods', backref=db.backref('communication_preferences', uselist=True))
  communication_frequency_id = db.Column(db.Integer, db.ForeignKey('communication_frequency.id'), nullable=False) 
  communication_frequency = db.relationship('CommunicationFrequency', backref=db.backref('communication_frequency', uselist=True))
  communication_time_id = db.Column(db.Integer, db.ForeignKey('communication_time.id'), nullable=False)
  communication_time = db.relationship('Communication_time', backref=db.backref('communication_time'), uselist=True)
  created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('EST')), onupdate=datetime.now(pytz.timezone('EST')), nullable=False)

  def __repr__(self) -> str:
    return '<Communication Preference %r' % self.id



############## STUDY GROUP SESSION HISTORY ###############
# Define a model that stores the user's history study group session
# query the group databases that contains the users profile  
# class StudyHistory(db.Model):
#   id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
#   user_id = db.Column(db.String(500), db.ForeignKey('users_information.id'), nullable=False)
#   group_id = db.Column(db.String(500), db.ForeignKey())
  


