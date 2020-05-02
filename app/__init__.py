import datetime
import json
import os
from datetime import date
from functools import wraps
from os import environ as env

import google_auth_oauthlib.flow
import requests as rq
from auth0.v3.authentication import Social
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import (Flask, Response, jsonify, redirect, render_template,
                   request, session, url_for, send_from_directory)
#from flask_cors import CORS
from google.auth import crypt, jwt
from google.auth.credentials import Credentials
from google.auth.transport import requests
from google.oauth2 import id_token
from googleapiclient.discovery import build
from six.moves.urllib.parse import urlencode
from werkzeug.exceptions import HTTPException

from app.dataAPI.academic_cal import (getAcademicCalendarInfo,
                                      getImportantEvents)
from app.dataAPI.auth0_api import getAuth0AppToken, getAuth0UserData
from app.dataAPI.course_methods import get_all_course_info
from app.dataAPI.user_cal_methods import (clean_recurrences,
                                          clear_multiple_classic_events,
                                          get_classic_generated_events,
                                          get_user_calendar_book,
                                          get_user_calendar_events,
                                          insert_user_calendar_events)

load_dotenv()
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")

APP = Flask(__name__, static_folder='../build', static_url_path='/')
APP.secret_key = AUTH0_CLIENT_SECRET
# CORS(APP)  # delete later


OAUTH = OAuth(APP)
# https://developers.google.com/calendar/v3/reference/events/insert
# https://dateutil.readthedocs.io/en/stable/rrule.html
auth0 = OAUTH.register(
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

if os.environ.get("DEPLOYED", "FALSE") == "TRUE":
    REDIRECT_URI = "https://classic-course-manager.herokuapp.com"
else:
    REDIRECT_URI = "http://localhost:5000"


def requires_auth(f):
    """Auth decorator for protected routes
    Args:
        f (incoming_request): undecorated request

    Returns:
        request: returns decorated request with session info
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)

    return decorated

###### PAGE ROUTES ######
@APP.route('/')
def index():
    """Index Route

    Returns:
        HTML File: GUI entry point for application
    """
    return APP.send_static_file('index.html')


@APP.route('/landing/<path>')
def send_resources(path):
    """Index Route

    Returns:
        HTML File: GUI entry point for application
    """
    return send_from_directory('/landing', path)


@APP.route('/dashboard')
@requires_auth
def dashboard():
    """Application Route

    Returns:
        React App: The main application
    """
    return APP.send_static_file('index.html')

###### AUTH ROUTES ######
@APP.route('/callback')
def callback_handling():
    """ Handles the code passed back by Auth0 so that we can authenticate the user

    Returns:
        Redirect: Redirects the authenticated user to the dashboard route
    """
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

    if ('google-idap' not in session
            and not AUTH0_APP_TOKEN["error"]):
        print("Getting IDAP")
        session['full_user_data'] = getAuth0UserData(
            AUTH0_APP_TOKEN["data"], session['profile']['user_id'])
        session['google-idap'] = session['full_user_data']["data"]["identities"][0]
    elif AUTH0_APP_TOKEN["error"]:
        print(AUTH0_APP_TOKEN["message"])

    return redirect('/dashboard')


@APP.route('/login')
def login():
    """Login route: generates the link needed to log into Auth0

    Returns:
        Redirect: Redirects user to the log in page
    """
    return auth0.authorize_redirect(
        redirect_uri=REDIRECT_URI + "/callback")


@APP.route('/logout')
def logout():
    """Log out route logs user out of Auth0 and ends session

    Returns:
        Redirect: Returns back to the static login entry point
    """
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {
        'returnTo': "http://classic-course-manager.surge.sh",
        'client_id': 'E8QL9VOgqinTgGL7rpgYjkVrWQWhecet'}
    return redirect("https://oakypokey.auth0.com" +
                    '/v2/logout?' + urlencode(params))

###### API ROUTES ######
@APP.route('/api/getinfo', methods=['POST'])
def get_info():
    """Retrieves course information from classy.thecorp.org

    Returns:
        Response: JSON object with courses that match search
    """
    values = request.json

    return Response(get_all_course_info(values), mimetype='application/json')


@APP.route('/api/getacademiccalinfo')
def get_academic_cal_info():
    """Gets academic calendar info from Google Calendar API

    Returns:
        Response: JSON with academic calendar events
    """
    return Response(json.dumps(getAcademicCalendarInfo()),
                    mimetype='application/json')


@APP.route('/api/user_data')
@requires_auth
def user_data():
    """Gets information about the user and returns it

    Returns:
        Response: JSON with user information
    """
    response = {}  # just to init
    # Store the user information in flask session.
    response["session"] = session['jwt_payload']
    response['full_user_data'] = session['full_user_data']
    response['user_calendar_book'] = get_user_calendar_book(
        session['google-idap']['access_token'])
    try:
        """
        response2 = get_user_calendar_events(
            session['google-idap']['access_token'], "cod11@georgetown.edu")

        response['calendar-book'] = response1
        response['calendar-events'] = response2
        insert_user_calendar_events(
            session['google-idap']['access_token'], {"id": "cod11@georgetown.edu"}, [1]) """

        response["academic_cal"] = getAcademicCalendarInfo()
        response["important_events"] = getImportantEvents()

    except Exception as e:
        print(e, e.__traceback__.tb_lineno)

    return Response(json.dumps(response), mimetype='application/json')


@APP.route('/api/user_events', methods=['POST'])
@requires_auth
def post_user_events():
    """Endpoint for users to post the events they want to add to their calendar

    Returns:
        Response: JSON with the success status of each event

    """
    body = request.json
    response = insert_user_calendar_events(
        session['google-idap']['access_token'],
        calendar_id=body['calendar_id'],
        events_array=body['basket'])
    response = {"data": response}

    response1 = clean_recurrences(
        session['google-idap']['access_token'], body['calendar_id'], False)
    return Response(json.dumps(response1), mimetype="application/json")


@APP.route('/api/clear_events', methods=['POST'])
@requires_auth
def clear_classic_events():
    """Clear events created by Classic for the associated calendar

    Returns:
        Response: JSON containing information about whether operation was successful

    """

    values = request.json

    if "calendar_id" not in values.keys():
        return Response(status=400)

    events = get_classic_generated_events(
        session['google-idap']['access_token'],
        values["calendar_id"])
    print([event['id'] for event in events])
    response = clear_multiple_classic_events(
        session['google-idap']['access_token'], values["calendar_id"], [
            event['id'] for event in events])
    response = {"data": response}
    response1 = json.dumps(response)
    return Response(response1, mimetype="application/json")


def create_app():
    """Starts the application

    Returns:
        FlaskApp: Returns the application itself
    """
    return APP
