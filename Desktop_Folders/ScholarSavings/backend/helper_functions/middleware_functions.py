# this is a middleware function that take a request and response to validate the token from the request to grant users access to protected resources that required authentication
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import pdb

def token_required(permissions_list):
 def decorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
   token = request.cookies.get('token')
   if not token:
    return jsonify({'message' : 'Token is missing!'}), 401
   try:
    data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    for permission in permissions_list:
     if permission not in data['permissions']:
      return jsonify({'message' : 'Unauthorized access!'}), 403
   except:
    return jsonify({'message' : 'Token is invalid!'}), 401
   return f(*args, *kwargs)
  return decorated_function
 return decorator