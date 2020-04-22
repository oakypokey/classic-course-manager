import os
from dotenv import load_dotenv, find_dotenv
import requests as rq
import json
from datetime import date
from app.dataAPI.academic_cal import getAcademicCalendarInfo, getImportantEvents
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
from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from google.auth import crypt
from google.auth import jwt
import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests
from app.dataAPI.user_cal_methods import get_user_calendar_book, get_user_calendar_events, insert_user_calendar_events
#from flask_cors import CORS
import datetime

load_dotenv()
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")

app = Flask(__name__ , static_folder='../build', static_url_path='/')
app.secret_key = AUTH0_CLIENT_SECRET

#CORS(app) #delete later


oauth = OAuth(app)
# https://developers.google.com/calendar/v3/reference/events/insert
# https://dateutil.readthedocs.io/en/stable/rrule.html
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

if(os.environ.get("DEPLOYED", "FALSE") == "TRUE"):
    REDIRECT_URI = "https://classic-course-manager.herokuapp.com"
else:
    REDIRECT_URI = "http://localhost:5000"

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

###### PAGE ROUTES ######
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@requires_auth
def dashboard():
    return app.send_static_file('index.html')

###### AUTH ROUTES ######
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
        session['full_user_data'] = getAuth0UserData(AUTH0_APP_TOKEN["data"], session['profile']['user_id'])
        user_data = session['full_user_data']["data"]["identities"][0]
        session['google-idap'] = user_data
        #session['google-idap']['expires_in'] = datetime.datetime.now() + session['google-idap']['expires_in']
    elif(AUTH0_APP_TOKEN["error"]):
        print(AUTH0_APP_TOKEN["message"])

    return redirect('/dashboard')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=REDIRECT_URI + "/callback")

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': REDIRECT_URI, 'client_id': 'E8QL9VOgqinTgGL7rpgYjkVrWQWhecet'}
    return redirect("https://oakypokey.auth0.com" + '/v2/logout?' + urlencode(params))

###### API ROUTES ######
@app.route('/api/getinfo', methods=['POST'])
def get_info():
    values = request.json

    return Response(getAllCourseInfo(values), mimetype='application/json')

@app.route('/api/getacademiccalinfo')
def get_academic_cal_info():
    return Response(json.dumps(getAcademicCalendarInfo()), mimetype='application/json')

@app.route('/api/user_data')
@requires_auth
def user_data():
    response = {} #just to init
    # Store the user information in flask session.
    response["session"] = session['jwt_payload']
    response['google-idap'] = session['google-idap']
    response['full_user_data'] = session['full_user_data']
    response['user_calendar_book'] = get_user_calendar_book(session['google-idap']['access_token'])
    try:
        #response1 = get_user_calendar_book(session['google-idap']['access_token'])
        #response2 = get_user_calendar_events(session['google-idap']['access_token'], "cod11@georgetown.edu")

        #response['calendar-book'] = response1
        #response['calendar-events'] = response2
        #insert_user_calendar_events(session['google-idap']['access_token'], {"id":"cod11@georgetown.edu"}, [1])

        response["academic_cal"] = getAcademicCalendarInfo()
        response["important_events"] = getImportantEvents()

        print(datetime.datetime.now().time().isoformat())
        
    except Exception as e:
        print(e, e.__traceback__.tb_lineno)

    return Response(json.dumps(response), mimetype='application/json')

@app.route('/api/user_events', methods= ['POST'])
@requires_auth
def post_user_events():
    print(request.json())
    #body = request.json()
    #response = insert_user_calendar_events(session['google-idap']['access_token'], calendar=body['calendar_id'], events_array=body['basket'])
    #return Response(json.dumps(response), mimetype='application/json')

###### HELPER METHODS ######
def getServiceAccountInfo():
    response = {
        "type": "",
        "project_id": "",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "",
        "client_x509_cert_url": ""
    }

    for key in response.keys():
        response[key] = os.environ.get(key, "")
    
    return response


def create_app():
    return app