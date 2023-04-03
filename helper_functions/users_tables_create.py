import pdb
# This is a helper function that helps create the registration table for users to register their email, username, password and phone number to become a diligent ScholarSaver!!!!!!
def create_registration_table(app, inspector, db, engine) -> None:
 with app.app_context():
  try:
   # get all the tables in the database
   db.metadata.bind = engine
   table_names = inspector.get_table_names()
   # check first if the registration table is already existed
   if 'users' not in table_names or 'verification_methods' not in table_names or 'permission' not in table_names:
    db.metadata.tables['verification_methods'].create()
    db.metadata.tables['users'].create()
    db.metadata.tables['permission'].create()
    print(f"Registration tables have been created successfully!")
    return
  except:
   print(f"Registration tables already existed in the database!")

# This is a helper function that helps to create 3 tables when the users choose to use machine learning algorithm for making saving challenges and strategies
all_tables_names = ['gender', 'users_information', 'institutions', 'degree', 'majors', 'identification', 'education', 'study_environment', 'study_location', 'study_time', 'study_session', 'study_techniques', 'collaboration', 'learning_styles', 'study_methodology', 'study_materials', 'study_preferences', 'availability_schedule', 'long_term_goal', 'communication_methods', 'communication_frequency', 'communication_time', 'communication_preferences']

def create_users_tables(app, inspector, db, engine) -> None:
 with app.app_context():
  try:
   # get all the tables in the database
   db.metadata.bind = engine
   table_names = inspector.get_table_names()
   for i in all_tables_names:
    if i not in table_names:
     db.metadata.tables[i].create()
   # Check if the constraint already exists on the 'users' table
   constraints = inspector.get_check_constraints('users_information')
   for constraint in constraints:
    if constraint['name'] == 'age_check':
      print(f"The 'age_check' constraint already exits on the 'users' table")
      break
    else: 
      # Add the constraint if it does not already exist
      db.engine.execute('ALTER TABLE users ADD CONSTRAINT age_check CHECK(age >=18)')
      db.engine.execute('ALTER TABLE users ADD CONSTRAINT age_check CHECK (age = extract(year from age(date_of_birth)))')
      print(f"Added the 'age_check' constraint to the 'users' table.")
    print(f"All tables created successfully!")
    return
  except:
    print (f"Gender, Identification and Users already existed in the database!")