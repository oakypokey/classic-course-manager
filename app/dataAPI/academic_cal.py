from __future__ import print_function
import datetime
from dateutil.parser import parse as datetimeparse
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import json
import os

load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


def getImportantEvents():
    academicCal = getAcademicCalendarInfo()
    importantEvents = []
    result = {}

    if academicCal["error"]:
        return

    # First get the semester start and end dates
    for event in academicCal["events"]:
        if event["summary"].find("Classes Begin") != -1:
            importantEvents.append(event)

        if event["summary"].find("Classes End") != -1:
            importantEvents.append(event)

        if event["summary"].find("Holiday:") != -1:
            importantEvents.append(event)

        if event["summary"].find("Thanksgiving") != -1:
            importantEvents.append(event)

        if event["summary"].find("Spring Break") != -1:
            importantEvents.append(event)

        if event["summary"].find("Classes Resume") != -1:
            importantEvents.append(event)

        if event["summary"].find("Easter") != -1:
            importantEvents.append(event)

    result["important_events"] = importantEvents

    # Calculate blacklisted days
    fall_semester = []
    spring_semester = []
    holidays = []

    for event in importantEvents:
        event_date = datetimeparse(event['start']['datetime'])

        if (event_date.month > 7):
            fall_semester.append(event)

        else:
            spring_semester.append(event)

        if event['summary'].find("Holiday") != -1:
            holidays.append(event['start']['datetime'])

    periods = {
        "fall_semester": getStartEnd(fall_semester),
        "spring_semester": getStartEnd(spring_semester)
    }

    result["periods"] = periods

    result["holidays"] = holidays

    return result


def getStartEnd(events):
    result = {}
    for event in events:
        if(str.lower(event['summary']).find("classes begin") != -1):
            result["start"] = event

        if(str.lower(event['summary']).find("classes end") != -1):
            result["end"] = event

    return result


def getAcademicCalendarInfo():
    try:
        response = {}
        success = False
        response = readFromFile()

        if 'error' in response:
            if(response['error'] == True):
                print(response["message"], ". Fetching new data...")
                response = makeAcademicCalApiCall()
                success = writeToFile(response)

        age = datetime.datetime.now().timestamp(
        ) - datetimeparse(response['last_fetched']).timestamp()

        if (age > (60 * 60 * 23)):  # update every 24 hours lol
            response = makeAcademicCalApiCall()
            if(response['error'] == True):
                raise Exception("response['message']")
            success = writeToFile(response)

        if(success == False):
            print("File was not updated.")

        return response

    except Exception as e:
        print("[getAcademicCalendarInfo] Error: ", e)
        return({"error": True, "message": e})


def readFromFile():
    try:
        if os.path.exists('academic_cal.pickle'):
            print("Reading from file...")
            with open('academic_cal.pickle', 'rb') as academic_cal_file:
                cachedResponse = pickle.load(academic_cal_file)
            return cachedResponse
        else:
            return {"error": True, "message": "File not found"}

    except Exception as e:
        print("readFromFile Error: ", e)
        return {"error": True, "message": e}


def writeToFile(content):
    try:
        with open('academic_cal.pickle', 'wb') as academic_cal_file:
            pickle.dump(content, academic_cal_file)

        print("File was updated.")
        return True
    except Exception as e:
        print("writeToFile Error: ", e)
        return False


def makeAcademicCalApiCall():
    try:
        currentYear = datetime.datetime.now().year
        OPTIONS = {
            "calendarId": "georgetown.edu_5bdj87g8237emjmvigu4rak1is@group.calendar.google.com",
            "orderBy": "startTime",
            "singleEvents": "true",
            "timeMin": str(currentYear) + "-08-01T00:00:00Z",
            "timeMax": str(currentYear + 1) + "-08-01T00:00:00Z"
        }

        calendar_service = build(
            'calendar', 'v3', developerKey=GOOGLE_API_KEY)

        # pylint: disable=no-member
        academic_events = calendar_service.events().list(
            calendarId=OPTIONS["calendarId"],
            orderBy=OPTIONS["orderBy"],
            singleEvents=True,
            timeMin=OPTIONS["timeMin"],
            timeMax=OPTIONS["timeMax"]).execute()

        eventsList = {
            "last_fetched": datetime.datetime.now().isoformat(),
            "events": [],
            "error": False
        }

        for event in academic_events["items"]:
            if 'summary' not in event:
                event["summary"] = "No summary found."

            if 'description' not in event:
                event["description"] = "No description found"

            if 'date' in event['start']:
                event['start']['datetime'] = event['start']['date']

            if 'date' in event['end']:
                event['end']['datetime'] = event['end']['date']

            eventsList["events"].append({
                "start": event["start"],
                "end": event["end"],
                "summary": event["summary"],
                "description": event["description"]
            })

        return eventsList

    except Exception as e:
        return {
            "error": True,
            "message": e
        }
