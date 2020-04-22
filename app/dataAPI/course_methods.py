import requests
import json
from app.dataAPI.academic_cal import getAcademicCalendarInfo
from dateutil.rrule import rrule, DAILY

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
def getCourseInfo(values):
    data = BASE_OPTIONS.copy()
    data["crn"] = values['crn']
    data['class_name'] = values['class_name']
    data['prof_name'] = values['prof_name']
    data['department'] = values['dep_name']

    response = requests.post(BASE_URL, data=data)
    return response.json()

## Get course timings
def getMoreCourseInfo(crn):
    result = {"error": "false"}
    response = requests.get("https://classy.thecorp.org/get-event-source/" + str(crn))
    result["data"] = json.loads(response.text)

    # freq, dtstart, until, wkst
    print(rrule(freq=DAILY))

    print(result)
    return result

#Bundle and format
def getAllCourseInfo(values):
    info = getCourseInfo(values)

    if info["error"]:
        print(info)
        return info

    for result in info['results']:
        result['timings'] = getMoreCourseInfo(result["crn"])["data"]

    return json.dumps(info)