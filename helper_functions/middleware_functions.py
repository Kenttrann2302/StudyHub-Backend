# this is a middleware function that take a request and response to validate the token from the request to grant users access to protected resources that required authentication
import json
from functools import wraps

import jwt
from flask import Response, request


def token_required(permission_list, secret_key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get("token")
            if not token:
                response_data = {"message": "Token is missing in cookies"}
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json, status=401, mimetype="application/json"
                )
                return response

            try:
                data = jwt.decode(token, secret_key, algorithms=["HS256"])
                for permission in permission_list:
                    if permission not in data["permissions"]:
                        response_data = {"message": "Unauthorized accessed!"}
                        response_json = json.dumps(response_data)
                        response = Response(
                            response=response_json,
                            status=403,
                            mimetype="application/json",
                        )
            except:
                response_data = {"message": "Token is invalid!"}
                response_json = json.dumps(response_data)
                response = Response(
                    response=response_json, status=400, mimetype="application/json"
                )
                return response
            return f(*args, *kwargs)

        return decorated_function

    return decorator
