########## SIGN UP PAGE #########
# import libraries 
from flask import Flask, redirect, url_for, render_template
import sqlite3 as sql
from flask_sqlalchemy import SQLAlchemy
import psycopg2

# connect flask to postgres database using SQLALCHEMY
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kenttran@localhost:5432/userdatabase'
# db = SQLAlchemy(app)

# CONNECT FLASK TO POSTGRESQL
conn = psycopg2.connect(
  host = "localhost",
  database = "userdatabase",
  user = "kenttran",
  password = None
)
print("Opened database successfully")

# CREATE A CURSOR OBJECT
cursor = conn.cursor()

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

class signUpForm:

  def __init__(self) -> None:
    pass

  def createdb(self) -> None:
    # CREATE A TABLE FOR GENDER OPTIONS
    create_gender_sql = '''
      CREATE TABLE IF NOT EXISTS gender(
        id INT PRIMARY KEY,
        gender_options VARCHAR(50) NOT NULL
      );
    '''
    # INSERT VALUE INTO GENDER TABLE
    insert_gender_sql = '''
      INSERT INTO gender(id, gender_options)
      VALUES (1, 'MALE'), (2, 'FEMALE'), (3, 'OTHERS'), (4, 'PREFER NOT TO TELL');
    '''
    # CREATE A TABLE FOR IDENTIFICATION OPTIONS
    create_identification_sql = '''
      CREATE TABLE IF NOT EXISTS identification(
        id INT PRIMARY KEY,
        identification_options VARCHAR(50) NOT NULL
      );
    '''
    # INSERT VALUE INTO IDENTIFICATION TABLE
    insert_identification_sql = '''
      INSERT INTO identification(id, identification_options)
      VALUES (1, 'PASSPORT'), (2, 'DRIVER LICENSE');
    '''
    # CREATE A TABLE FOR USERS DATA
    create_users_sql = '''
      CREATE TABLE IF NOT EXISTS users(
        id INT PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        middle_name VARCHAR(100),
        last_name VARCHAR(100) NOT NULL,
        age INT NOT NULL CHECK (age >= 18 AND age <= 99),
        date_of_birth DATE NOT NULL,
        address_line_1 VARCHAR(500) NOT NULL,
        address_line_2 VARCHAR(500),
        city VARCHAR(50) NOT NULL,
        country VARCHAR(50) NOT NULL,
        postal_code VARCHAR(10) NOT NULL,
        gender_id INT NOT NULL,
        FOREIGN KEY (gender_id) REFERENCES gender(id),
        religion VARCHAR(100), 
        identification_id INT NOT NULL,
        FOREIGN KEY (identification_id) REFERENCES identification(id),
        passport INT CHECK (passport >= 100000000 AND passport <= 999999999),
        driver_license INT CHECK (driver_license >= 10000 AND driver_license <= 99999)
      );
    '''

    
    cursor.execute(create_gender_sql)
    print("Table created successfully")
    cursor.execute(insert_gender_sql)
    cursor.execute(create_identification_sql)
    print("Table created successfully")
    cursor.execute(insert_identification_sql)
    cursor.execute(create_users_sql)
    print("Table created successfully")
    conn.commit()
    conn.close()
  
  @app.route('/mycibc/signUP/')
  def render_signup(self) -> None:
    with app.app_context():
      # get all of the gender options
      cursor.execute("SELECT * FROM gender;")
      genders = cursor.fetchall()

      # get all of the identification options
      cursor.execute("SELECT * FROM identification;")
      identifications = cursor.fetchall()

      return render_template('signUP.html', gender_options=genders)


  
  