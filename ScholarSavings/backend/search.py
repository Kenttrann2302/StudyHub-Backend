# THIS FILE WILL TRIGGER THE SEARCH URL WHEN THE USERS CLICK ON THE SEARCH ICON IN THE MAIN HOME PAGE
# find all the keywords in the website so the users can search easier
from flask import Flask, url_for, render_template, redirect, request, send_from_directory
from flask_restful import Api, Resource, reqparse
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import pdb

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
api = Api(app)

# Global dictionary mapping search result items to their URLs
item_urls = {
 'homepage': '/home/',
 'HomePage': '/home/',
 'home page': '/home/',
 'home': '/home/',
 'Home': '/home/',
 'signup': '/scholarsavings/treasurehunt/signup/',
 'register': '/scholarsavings/register/',
 'Signup': '/hcm/signup/',
 'sign up': '/hcm/signup/',
 'SIGN UP': '/hcm/signup/',
 'sign UP': '/hcm/signup/'
}

# function to search for the item and return the match array
def search(query, items) -> list:
 matches = []
 for item in items:
  if query is not None and query.lower() in item.lower():
   matches.append(item)
 return matches

class searchItemsResource(Resource):
 def __init__(self) -> None:
  super().__init__()

 def search_results(self) -> None:
  with app.app_context():
   query = request.args.get('query')
   # Implement the search logic
   # Find matches in the dictionary keys
   matches = search(query, item_urls.keys())
   # Create a dictionary where keys are unique URLs and values are corresponding titles
   url_title_dict = {}
   for result in matches:
    link = item_urls[result]
    if link not in url_title_dict:
     # append the key and the value of that key into the url_title_dict map
     url_title_dict[link] = result

   # Render search results in HTML
   return render_template('search.html', query=query, unique_links=url_title_dict)

api.add_resource(searchItemsResource, '/scholarsavings/search/')