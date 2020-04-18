import requests
import json
from app.dataAPI.academic_cal import getAcademicCalendarInfo

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