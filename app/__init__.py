import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
import requests
import json
from datetime import date
from app.dataAPI.academic_cal import getAcademicCalendarInfo

load_dotenv()

#API Methods
## Setting variables
BASE_URL = "https://classy.thecorp.org/search-submit/"
BASE_OPTIONS = {
  "class_name": '',
  "prof_name": '',
  "department": '',
  'x-list': '',
  "reqs": '',
  "day_0": 'on',
  "day_1": 'on',
  "day_2": 'on',
  "day_3": 'on',
  "day_4": 'on',
  "day_5": 'on',
  "day_6": 'on',
  "between_hours": '8:00 AM - 11:00 PM',
  "crn": ""
}

## Get course information
def getCourseInfo(crn):
    data = BASE_OPTIONS.copy()
    data["crn"] = crn
    response = requests.post(BASE_URL, data=data)
    return response.json()

## Get course timings
def getMoreCourseInfo(crn):
    result = {"error": "false"}
    response = requests.get("https://classy.thecorp.org/get-event-source/" + str(crn))
    result["data"] = json.loads(response.text)
    print(result)
    return result

#Bundle and format
def getAllCourseInfo(crn):
    info = getCourseInfo(crn)

    for result in info['results']:
        result['timings'] = getMoreCourseInfo(result["crn"])["data"]

    return json.dumps(info)

#END API METHODS

app = Flask(__name__, static_folder='../build', static_url_path='/')

@app.route('/')
def index():
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
    

def create_app():
    return app