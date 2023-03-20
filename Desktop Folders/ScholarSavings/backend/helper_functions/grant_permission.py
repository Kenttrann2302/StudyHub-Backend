# this is a helper function that will grant the permission for the users to access to limited resources after they have verified their account with AWS SNS
from flask import Flask
from database.users_models import db, Users, Permission

permission_app = Flask(__name__)
db.init_app(permission_app)

def grant_permission_to_verified_users(permission_name) -> None:
 # query to get all the users who have verified their account
 verified_users = Users.query.filter_by(account_verified=True).all()

 # grant the access to view the user dashboard, allow them to sign up for the saving challenges game to these users
 for user in verified_users:
  permission = Permission.query.filter_by(user_id=user.user_id, name=permission_name).first()
  if not permission:
   permission = Permission(name=permission_name, user_id=user.user_id)
   db.session.add(permission)

 db.session.commit()
