from flask import Flask, url_for, render_template, redirect
from signup import signUpForm

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# rendering the homepage
@app.route('/home/')
def mainHomePage():
  return render_template('main_homepage.html')

# create an object to signup
signUP = signUpForm()
signUP.createdb()
signUP.render_signup()

if __name__ == '__main__':
  app.run(debug=True)