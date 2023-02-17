########## SIGN UP PAGE #########
# import libraries 
from flask import Flask, redirect, url_for, render_template, jsonify, request
import sqlite3 as sql
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import pdb

# import other files
from API.locationAPI import checkAddress

# connect flask to postgres database using SQLALCHEMY
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
# db = SQLAlchemy(app)

# CONNECT FLASK TO POSTGRESQL
connection = psycopg2.connect(
  host = "localhost",
  database = "userdatabase",
  user = "kenttran",
  password = None
)
print("Opened database successfully")

# CREATE A CURSOR OBJECT
cursor = connection.cursor()

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

class signUpForm:
  def __init__(self) -> None:
    pass

  def add_gender_table(self) -> None:
    # CREATE A TABLE FOR GENDER OPTIONS
    create_gender_sql = '''
      CREATE TABLE IF NOT EXISTS gender(
        id INT PRIMARY KEY,
        gender_options VARCHAR(50) NOT NULL
      );
    '''
    cursor.execute(create_gender_sql)
    print(" Gender Table created successfully!")

    # create a list of tuple values to add to the rows:
    gender_list = [(1, 'MALE'), (2, 'FEMALE'), (3, 'OTHERS'), (4, 'PREFER NOT TO TELL')]

    # CHECK IF THE ROWS EXIST BEFORE INSERTING INTO THE ROWS
    for gender_id, gender_name in gender_list:
      select_gender_sql = '''
        SELECT id FROM gender WHERE id=%s;
      '''
      cursor.execute(select_gender_sql, (gender_id,))
      row = cursor.fetchone()
      # if the row not exist -> add row
      if row is None:
        insert_gender_id = '''
          INSERT INTO gender (id, gender_options)
          VALUES (%s,%s);
        '''
        cursor.execute(insert_gender_id, (gender_id, gender_name))
      # else:
      #   update_gender_sql = '''
      #     UPDATE gender SET gender_options=%s WHERE id=%s
      #   '''
      #   cursor.execute(update_gender_sql, (gender_name, gender_id))
    
    connection.commit()


  def add_identification_table(self) -> None:
    # CREATE A TABLE FOR IDENTIFICATION OPTIONS
    create_identification_sql = '''
      CREATE TABLE IF NOT EXISTS identification(
        id INT PRIMARY KEY,
        identification_options VARCHAR(50) NOT NULL
      );
    '''
    cursor.execute(create_identification_sql)
    print("Identification Table was created successfully!")

    # create a list of tuple values to add to the rows
    identification_list = [(1, '--select--'), (2, 'PASSPORT'), (3, 'DRIVER LICENSE')]

    # CHECK IF THE ROWS ALREADY EXISTED BEFORE ADDING TO THE ROWS
    for identification_id, identification_name in identification_list:
      select_identification_sql = '''
        SELECT id FROM identification WHERE id=%s;
      '''
      cursor.execute(select_identification_sql, (identification_id,))
      row = cursor.fetchone()
      # if the row exists -> add row
      if row is None:
        insert_identification_id = '''
          INSERT INTO identification (id, identification_options)
          VALUES (%s, %s);
        '''
        cursor.execute(insert_identification_id, (identification_id, identification_name))

      connection.commit()

  def create_user_table(self) -> None:
    # CREATE A TABLE FOR USERS DATA
    create_users_sql = '''
      CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        middle_name VARCHAR(100),
        last_name VARCHAR(100) NOT NULL,
        age INT NOT NULL CHECK (age >= 18 AND age <= 99),
        date_of_birth DATE NOT NULL,
        address_line_1 VARCHAR(500) NOT NULL,
        address_line_2 VARCHAR(500),
        city VARCHAR(50) NOT NULL,
        province VARCHAR(50) NOT NULL,
        country VARCHAR(50) NOT NULL,
        postal_code VARCHAR(10) NOT NULL,
        gender_id INT NOT NULL,
        FOREIGN KEY (gender_id) REFERENCES gender(id),
        religion VARCHAR(100), 
        identification_id INT NOT NULL,
        FOREIGN KEY (identification_id) REFERENCES identification(id),
        identification_number INT NOT NULL,
        isRegister BOOLEAN NOT NULL DEFAULT FALSE
      );
    '''

    cursor.execute(create_users_sql)
    print("Table created successfully")

    # Add the constraints relationship between the age and the birthday
    createEnforceFunction = '''
      CREATE OR REPLACE FUNCTION enforce_age_constraint() RETURNS TRIGGER AS $$ 
      BEGIN
        IF NEW.age != (EXTRACT(YEAR FROM AGE(NEW.date_of_birth)))::integer THEN 
          RAISE EXCEPTION 'Age must be equal to current year minus birthday year';
        END IF;
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;
    '''

    triggerEnforceFunction = '''
      CREATE OR REPLACE TRIGGER enforce_age_constraint_trigger
        BEFORE INSERT OR UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION enforce_age_constraint();
    '''

    cursor.execute(createEnforceFunction)
    cursor.execute(triggerEnforceFunction)
    print("Trigger function created successfully")

    connection.commit()
  
  # render the signup page -> front-end
  def render_signup(self) -> None:
    with app.app_context():
      # get all of the gender options
      cursor.execute("SELECT * FROM gender;")
      genders = cursor.fetchall()

      # get all of the identification options
      cursor.execute("SELECT * FROM identification;")
      identifications = cursor.fetchall()

      return render_template('signUP.html', gender_options = genders, identification_options = identifications)

  # perform action on the createaccount url 
  def createAccount(self):
    with app.app_context():
      
      # get the request method
      if request.method == 'POST':
        # get the users inputs
        try:
          firstName = request.form['fname']
          lastName = request.form['lname']
          midName = request.form['mname']
          age = request.form['age']
          birthDay = request.form['birthday']
          firstAddress = request.form['address1']
          secondAddress = request.form['address2']
          city = request.form['city']
          province = request.form['province']
          country = request.form['country']
          postalCode = request.form['postal_code']
          gender = request.form['gender_id']
          religion = request.form['religion']
          identification = request.form['identification_id']
          identification_number = request.form['id_number']

          # Check the constraint for the age and birthday of 
          
          # Validate the data and send it into the database
          ########!!!!!!! FIND A WAY TO VALIDATE THE DATA DEPEND ON THE REQUIREMENTS OF THE DATABASE OF EACH FIELD BEFORE SENDING TO THE DATABASE !!!!!!#########
          insert_users_statement = '''
            INSERT INTO users (
              first_name,
              middle_name,
              last_name,
              age,
              date_of_birth,
              address_line_1,
              address_line_2,
              city,
              province,
              country,
              postal_code,
              gender_id,
              religion,
              identification_id,
              identification_number
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
          '''
          
          # after getting the address, check for the validation using Googl Maps Geocoding API before execute the insert the element
          # if the address is not valid 
          addressChecking = checkAddress(firstAddress, city, province, country, postalCode, secondAddress)
          if not addressChecking.is_valid_address():
            print("Hello World")
            return redirect(url_for('signup'))

          # if the address is valid
          else:
            cursor.execute(insert_users_statement, (firstName, midName, lastName, age, birthDay, firstAddress, secondAddress, city, province, country, postalCode, gender, religion, identification, identification_number))

          connection.commit()
          if cursor.rowcount > 0:
            print("Data inserted successfully")
          else:
            print("Error inserting data")
          

        except Exception as e:  
          connection.rollback()
          print("Error: ", e)
          # rendering the form again to let the users to sign up again -> front-end
        
        finally:
          # render the successful page which gives the users their bank account information, check for register online banking and ask whether the users want to register for the online banking account
          return render_template("successful.html")
          connection.close()
      
          