import requests
import json
from app.dataAPI.academic_cal import getAcademicCalendarInfo, getImportantEvents
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse as datetimeparser
import datetime

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
    return result

#Bundle and format
def getAllCourseInfo(values):
    info = getCourseInfo(values)

    if info["error"]:
        print(info)
        return info

    print(info)

    for result in info['results']:
        result['timings'] = processDate(getMoreCourseInfo(result["crn"])["data"])

    
    return json.dumps(info)

def processDate(timings):
    important_dates = getImportantEvents()
    result = timings
    
    # figure out what semester it is
    now = datetime.datetime.now().timestamp()
    compare = []
    curr_sem = "N"

    for sem in important_dates['periods'].keys():
        processed = datetimeparser(important_dates['periods'][sem]['start']['start']['datetime'])
        compare.append({
            "value": abs(processed.timestamp() - now),
            "name": sem
        })    

    if(compare[0]['value'] > compare[1]['value']):
        curr_sem = compare[1]['name']
    else:
        curr_sem = compare[0]['name']
    
    current_important_dates = important_dates['periods'][curr_sem]

    for instance in result:
        gen_start_date = datetimeparser(current_important_dates["start"]["start"]["datetime"])
        weekdayNo = datetimeparser(instance['start']).weekday()
        start = datetimeparser(instance['start']).time().isoformat().split(".")[0].split(":")
        end = datetimeparser(instance['end']).time().isoformat().split(".")[0].split(":")

        test = gen_start_date.weekday()

        while test != weekdayNo:
            print(gen_start_date)
            gen_start_date = gen_start_date.replace(day=(gen_start_date.day - 1))
            test = gen_start_date.weekday()

        gen_start_time = gen_start_date
        gen_end_time = gen_start_date

        gen_start_time = gen_start_time.replace(hour=int(start[0]), minute=int(start[1]))
        gen_end_time = gen_end_time.replace(hour=int(end[0]), minute=int(end[1]))

        instance['start'] = gen_start_time.isoformat()
        instance['end'] = gen_end_time.isoformat()

    return result

