# this is a static file that get all the environment variables
# import libraries use
import os

# load in the sensitive data from .env
from dotenv import load_dotenv

# Load the configuration data from the .env file
load_dotenv()

# secret key
# get the secret key from the virtual environment
secret_key = os.getenv("STUDYHUB_SECRET_KEY")

# database stuffs
# get the database connection information
database_type = os.getenv("DB_TYPE")
database_host = os.getenv("DB_HOST")
database_username = os.getenv("DB_USER")
database_password = os.getenv("DB_PASS")
database_port = os.getenv("PORT")
database_name = os.getenv("DB_NAME")

# AWS stuffs
# get 2 apis for sending and verifying otp
aws_sending_otp = os.getenv("AWS_EMAIL_SEND_OTP")
aws_verify_otp = os.getenv("AWS_EMAIL_VERIFY_OTP")

# Google Cloud stuffs
google_api_secret_key = os.getenv("GOOGLE_GEOLOCATION_API")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
google_discovery_url = os.getenv("GOOGLE_DISCOVERY_URL")

# TWILIO stuffs
twilio_api_key = os.getenv("TWILIO_API_KEY")
