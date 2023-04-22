# this is a function using Twilio SendGrid Web API in order to send the email verification towards user's email address for verification method
from datetime import datetime, timedelta

import jwt
import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from get_env import secret_key, twilio_api_key


# function send the verification email along with the link for the user to verify their email address with StudyHub resource
def sendgrid_verification_email(user_email, studyhub_code) -> bool:
    # read the HTML template file
    with open("Twilio/twilio_email_template.html", "r") as f:
        template = f.read()

    # generate a JWT token that stores the user email address and the random otp string and valid for 10 minutes
    token = jwt.encode(
        {
            "email": user_email,
            "studyhub_code": studyhub_code,
            "exp": datetime.now(pytz.timezone("EST")) + timedelta(minutes=10),
        },
        secret_key,
        algorithm="HS256",
    )

    # replace the placeholders with the actual email and the studyhub_code value
    template = template.replace("{{token}}", token)

    # send the email using Twilio SendGrid
    message = Mail(
        from_email="studyhub2302@gmail.com",
        to_emails=user_email,
        subject="Verify your email address with StudyHub",
        html_content=template,
    )

    try:
        sg = SendGridAPIClient(twilio_api_key)
        response = sg.send(message)
        return (
            True,
            response,
            token,
        )  # return True indicated that the message has been sent successfully!
    except Exception as e:
        # return false indicates there was an error when send a verification email along with the error message and the status code
        return False, str(e), 500
