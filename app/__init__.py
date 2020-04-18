import os
from dotenv import load_dotenv, find_dotenv



import requests
import json
from datetime import date
from app.dataAPI.academic_cal import getAcademicCalendarInfo
from app.dataAPI.course_methods import getAllCourseInfo
from app.dataAPI.auth0_api import getAuth0AppToken
from app.dataAPI.auth0_api import getAuth0UserData
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import request
from flask import Response
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from oauthlib.oauth2 import BearerToken as bt

load_dotenv()
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")

app = Flask(__name__ , static_folder='../build', static_url_path='/')
app.secret_key = AUTH0_CLIENT_SECRET

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url='https://oakypokey.auth0.com',
    access_token_url='https://oakypokey.auth0.com/oauth/token',
    authorize_url='https://oakypokey.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

AUTH0_APP_TOKEN = getAuth0AppToken(AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET)

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@requires_auth
def dashboard():
    return app.send_static_file('index.html')

@app.route('/api/something')
def something():
    return {"foo": "bar"}

@app.route('/api/getinfo')
def get_info():
    return Response(getAllCourseInfo(request.args.get('crn', type = str)), mimetype='application/json')

@app.route('/api/getacademiccalinfo')
def get_academic_cal_info():
    return Response(json.dumps(getAcademicCalendarInfo()), mimetype='application/json')

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()


    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    if (('google-idap' not in session) and (not AUTH0_APP_TOKEN["error"] == True)):
        print("Getting IDAP")
        user_data = getAuth0UserData(AUTH0_APP_TOKEN["data"], session['profile']['user_id'])["data"]["identities"][0]
        session['google-idap'] = user_data['access_token']
    elif(AUTH0_APP_TOKEN["error"]):
        print(AUTH0_APP_TOKEN["message"])

    return redirect('/dashboard')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')


@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': "http://localhost:5000/", 'client_id': 'E8QL9VOgqinTgGL7rpgYjkVrWQWhecet'}
    return redirect("https://oakypokey.auth0.com" + '/v2/logout?' + urlencode(params))
    

@app.route('/api/user_data')
@requires_auth
def user_data():
    response = {} #just to init
    # Store the user information in flask session.
    response["session"] = session['jwt_payload']
    return Response(json.dumps(response), mimetype='application/json')


def create_app():
    return app