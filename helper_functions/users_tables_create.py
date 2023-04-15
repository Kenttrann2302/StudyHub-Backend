# helper function that creates all the tables inside the database
all_tables_names = ['users', 'permission', 'user_information', 'study_preferences', 'availability_schedule']

def create_all_tables(app, inspector, db, engine) -> None:
 with app.app_context():
  try:
   # get all the tables in the database
   db.metadata.bind = engine
   table_names = inspector.get_table_names()
   for i in all_tables_names:
    if i not in table_names:
     db.metadata.tables[i].create()
   # Check if the constraint already exists on the 'users' table
   constraints = inspector.get_check_constraints('user_information')
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
  except Exception as e:
    print(f"There was an error occured while creating all the tables in the database: {e}")