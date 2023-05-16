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


## Features

<!-- List the features of your application or follow the template. Don't share the figma file here :) -->

- User Registration and Authentication: StudyHub provides a user-friendly registration process and secure authentication mechanism, allowing users to create accounts and access the platform securely.
<img width="1685" alt="Screenshot 2023-05-15 at 10 58 04 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/3d65f58a-388e-4a36-8174-e675c4a73549">
- User Profiles and Preferences: Users can create personalized profiles, including study preferences, courses, and availability schedules. This information is used to match users with compatible study groups.
<img width="1694" alt="Screenshot 2023-05-15 at 11 03 18 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/41235b43-aa66-4f62-bb74-467821085aba">
- Study Group Matching Algorithm: StudyHub employs a neural network-based matching algorithm that analyzes user preferences and behavior to suggest the most suitable study groups. This algorithm ensures optimal group formations based on compatibility factors.
- Google OAuth 2.0 Integration: StudyHub integrates with Google OAuth 2.0 for seamless user authentication, enabling users to sign in using their Google accounts.
<img width="1694" alt="Screenshot 2023-05-15 at 11 04 29 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/5a2203f5-c324-4ab6-a30d-b4a03cd5eaab">
- Email Verification: To ensure the authenticity of user accounts, StudyHub incorporates email verification functionality. Users receive email notifications to verify their email addresses during the registration process, this is done by using AWS SES and Twilio SendGrid.
<img width="1371" alt="Screenshot 2023-05-15 at 11 07 29 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/26498a18-2537-4da8-be67-8b1d0ba0cd54">

<img width="1367" alt="Screenshot 2023-05-15 at 11 07 06 PM" src="https://github.com/Kenttrann2302/StudyHub-Backend/assets/110959350/b46bfc00-fe75-47b0-a21b-04b96f245d61">

- API Security: StudyHub implements API security best practices, including JWT tokens and bcrypt hashing, to protect sensitive user data and ensure secure communication between the client and server.
- Docker Containerization: The application is containerized using Docker, providing an isolated and portable environment for seamless deployment and scalability.
- AWS and GCP Integrations: StudyHub integrates with AWS services such as DynamoDB, Lambda, and SES for email delivery, along with GCP Geolocation API for address verification.
- Unit Testing: The codebase includes comprehensive unit tests for the REST APIs, ensuring functionality, reliability, and maintainability.


## How To Use

