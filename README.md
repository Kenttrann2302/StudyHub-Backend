<!-- Please update value in the {}  -->

<h1 align="center">StudyHub-Backend</h1>

<!-- TABLE OF CONTENTS -->

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
  - [Built With](#built-with)
- [Architecture](#architecture)
- [Features](#features)
- [How To Use](#how-to-use)
  - [How to run the server with docker commands](#set-up-dev-environment)
    - [Backend](#backend)
- [Common Issues](#common-issues)

<!-- OVERVIEW -->

## Overview

StudyHub is an online tool that facilitates the development of efficient and productive study groups. It strives to bring together students who have similar study preferences, courses, and locations in order to improve collaborative learning experiences.


### Built With

<!-- This section should list any major frameworks that you built your project using. Here are a few examples.-->

- [Flask](https://flask.palletsprojects.com/en/2.2.x/)
- [PostgreSQL](https://www.postgresql.org/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/)
- [Flask-Restful](https://flask-restful.readthedocs.io/en/latest/)


## Architecture

- Below is the snippet of the UML Diagram of our server:
<img width="1388" alt="Screenshot 2023-05-16 at 10 09 30 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/3770ea50-7b7a-4525-a03f-9516653ace51">


## Features

<!-- List the features of your application or follow the template. Don't share the figma file here :) -->

- User Registration and Authentication: StudyHub provides a user-friendly registration process and secure authentication mechanism, allowing users to create accounts and access the platform securely:
<img width="1685" alt="Screenshot 2023-05-15 at 10 58 04 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/3d65f58a-388e-4a36-8174-e675c4a73549">


- User Profiles and Preferences: Users can create personalized profiles, including study preferences, courses, and availability schedules. This information is used to match users with compatible study groups:
<img width="1694" alt="Screenshot 2023-05-15 at 11 03 18 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/41235b43-aa66-4f62-bb74-467821085aba">


- Study Group Matching Algorithm: StudyHub employs a neural network-based matching algorithm that analyzes user preferences and behavior to suggest the most suitable study groups. This algorithm ensures optimal group formations based on compatibility factors.


- Google OAuth 2.0 Integration: StudyHub integrates with Google OAuth 2.0 for seamless user authentication, enabling users to sign in using their Google accounts:
<img width="1694" alt="Screenshot 2023-05-15 at 11 04 29 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/5a2203f5-c324-4ab6-a30d-b4a03cd5eaab">


- Email Verification: To ensure the authenticity of user accounts, StudyHub incorporates email verification functionality. Users receive email notifications to verify their email addresses during the registration process, this is done by using AWS SES and Twilio SendGrid:
<img width="1371" alt="Screenshot 2023-05-15 at 11 07 29 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/26498a18-2537-4da8-be67-8b1d0ba0cd54">
<img width="1367" alt="Screenshot 2023-05-15 at 11 07 06 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/b46bfc00-fe75-47b0-a21b-04b96f245d61">


- API Security: StudyHub implements API security best practices, including JWT tokens and bcrypt hashing, to protect sensitive user data and ensure secure communication between the client and server.


- Docker Containerization: The application is containerized using Docker, providing an isolated and portable environment for seamless deployment and scalability:
<img width="1364" alt="Screenshot 2023-05-15 at 11 09 38 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/84d71120-7a8a-47b3-84f8-5e2ff870ae19">


- AWS and GCP Integrations: StudyHub integrates with AWS services such as DynamoDB, Lambda, and SES for email delivery, along with GCP Geolocation API for address verification:
<img width="1192" alt="Screenshot 2023-05-15 at 11 12 53 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/d3286ad1-dfe8-4e0f-bf12-d107389b5289">


- Unit Testing: The codebase includes comprehensive unit tests for the REST APIs, ensuring functionality, reliability, and maintainability.


## For development purpose:

Note: If you're using Windows, please clone this repo in WSL and run the docker commands in there.

To clone and run this application you'll need:
- [Git](https://git-scm.com)
- [Docker](https://docs.docker.com/get-docker/)

Then on your terminal, run the following from the root of this repository:

```bash
# Build the images and containers then run the containers
docker compose up -d --build
```

In order to test the APIs of each endpoint at http://0.0.0.0:8080/, use Postman collections.


To stop the containers and to start the containers after the initial build:

```bash
# For stopping and removing the containers created above
# Use the -v flag to remove the associated volumes
docker compose down

# For creating and starting the container
# after the initial build
docker compose up -d
```

### Good-to-Know Commands

**Run command in a container**

To run shell command in any of the two containers:

```bash
docker compose exec <service-name> <command> <list-of-args>

# Example: Running SQL commands in the container
PGPASSWORD=<password> psql -U <username> <database>

# Example: Make backend migrations with Flask Migrations
docker compose exec backend flask db init
docker compose exec backend flask db migrate -m <migration-message>
docker compose exec backend flask db upgrade
```

> We recommend creating alias(es) to shorten the above commands


## Common Issues

**Database is not up to date after running migration scripts**

```bash
# By running this command, the database will be up to date with the latest migration
docker compose exec backend flask db stamp head
```

**Import "{framework/library-name}" could not be resolved error from Pylance**

If you're using VSCode and see this error. This mean the framework/library was not installed globally or installed in the virtual environment you're using. We highly recommend setting up a new virtual environment. So remove your existing environment in the root of this repository. Then run the following commands

```bash
# Ensure you are in the root of this repository
python3 -m venv env # Our gitignore assumes the virtual environment name is env
source env/bin/activate
pip install -r backend/requirements.txt
```

Then select the interpreter in `env/bin/`. The issue should disappears.

Note: We assumed you're using MacOS or Linux. For Windows, please find the corresponding command for setting up Python virtual environment.
