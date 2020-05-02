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
    """Uses academic calendar information to determine holidays and semester periods

    Returns:
        dict: list of all important events, periods of fall and spring semester, and list of blacklisted dates
    """

    academicCal = getAcademicCalendarInfo()
    importantEvents = []
    result = {}

    # Checks to see that we actually have academic calendar information
    if academicCal["error"]:
        return

    # Get all the important dates that we are looking for in the calendar
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

    # Calculate semester periods
    fall_semester = []
    spring_semester = []
    holidays = []

    # Checks to see which events fall in which semester
    for event in importantEvents:
        event_date = datetimeparse(event['start']['datetime'])

        if (event_date.month > 7):
            fall_semester.append(event)

        else:
            spring_semester.append(event)

        if event['summary'].find("Holiday") != -1:
            holidays.append(event['start']['datetime'])

    # Get the start and end periods
    periods = {
        "fall_semester": getStartEnd(fall_semester),
        "spring_semester": getStartEnd(spring_semester)
    }

    # Get Thanksgiving dates
    thanksgiving_period = [event for event in fall_semester if event["summary"].find(
        "Thanksgiving") != -1 or event["summary"].find("Classes Resume") != -1]

    # Get Spring Break dates
    springbreak_period = [event for event in spring_semester if event["summary"].find(
        "Spring Break") != -1 or (event["summary"].find("Classes Resume") != -1 and event['start']['datetime'].split("-")[1] == "03")]

    # Get East Break dates
    easterbreak_period = [event for event in spring_semester if event["summary"].find(
        "Easter") != -1 or (event["summary"].find("Classes Resume") != -1 and event['start']['datetime'].split("-")[1] == "04")]

    if len(thanksgiving_period) == 2 and len(springbreak_period) == 2 and len(easterbreak_period) == 2:
        # Processing spring break and thanksgiving break as they follow the same school policy
        for breakperiod in [thanksgiving_period, springbreak_period]:
            start = datetimeparse(
                breakperiod[0]["start"]["datetime"]) + datetime.timedelta(days=1)
            end = datetimeparse(breakperiod[1]["start"]["datetime"])

            while start != end:
                holidays.append(start.strftime("%Y-%m-%d"))
                start = start + datetime.timedelta(days=1)

        # Processing east break dates
        easter_start = datetimeparse(
            easterbreak_period[0]["start"]["datetime"])
        easter_end = datetimeparse(easterbreak_period[1]["start"]["datetime"])

        while easter_start != easter_end:
            holidays.append(easter_start.strftime("%Y-%m-%d"))
            easter_start = easter_start + datetime.timedelta(days=1)
    else:
        print("Break period arrays are not long enough.")

    result["periods"] = periods

    result["holidays"] = holidays

    return result


def getStartEnd(events):
    """Semester periods helper function

    Args:
        events (list): important events within a given semester

    Returns:
        dict: contains start and end information for a semester
    """
    result = {}
    for event in events:
        if(str.lower(event['summary']).find("classes begin") != -1):
            result["start"] = event

        if(str.lower(event['summary']).find("classes end") != -1):
            result["end"] = event

    return result


def getAcademicCalendarInfo():
    """Attempts to retrieve academic cal information from file before making request

    Returns:
        dict: dict with all the academic cal events under attr 'events'
    """

    try:
        response = {}
        success = False
        response = readFromFile()

        # If reading from file fails, make a call
        if 'error' in response:
            if(response['error'] == True):
                print(response["message"], ". Fetching new data...")
                response = makeAcademicCalApiCall()
                success = writeToFile(response)

        age = datetime.datetime.now().timestamp(
        ) - datetimeparse(response['last_fetched']).timestamp()

        # Expiry of information. Update academic cal information every 24 horus
        if (age > (60 * 60 * 23)):
            response = makeAcademicCalApiCall()
            if(response['error'] == True):
                raise Exception(response['message'])
            success = writeToFile(response)

        # See if the file was updated or not in console
        if(success == False):
            print("File was not updated.")

        return response

    except Exception as e:
        # Error? Return error and message
        print("[getAcademicCalendarInfo] Error: ", e)
        return({"error": True, "message": e})


def readFromFile():
    """Reads academic calendar info from file

    Returns:
        dict: dict with all the academic cal events under attr 'events'
    """
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
    """Pickles academic cal response for later use

    Args:
        content (dict): dict with all the academic cal events under attr 'events'

    Returns:
        bool: whether or not the operation was successful
    """
    try:
        with open('academic_cal.pickle', 'wb') as academic_cal_file:
            pickle.dump(content, academic_cal_file)

        print("File was updated.")
        return True
    except Exception as e:
        print("writeToFile Error: ", e)
        return False


def makeAcademicCalApiCall():
    """Makes a call to the Google Cal API to get academic cal events. Academic cal owned by georgetown

    Returns:
        dict: dict with all the academic cal events under attr 'events'
    """
    try:
        # Only get events for the upcoming year
        currentYear = datetime.datetime.now().year
        OPTIONS = {
            "calendarId": "georgetown.edu_5bdj87g8237emjmvigu4rak1is@group.calendar.google.com",
            "orderBy": "startTime",
            "singleEvents": "true",
            "timeMin": str(currentYear) + "-08-01T00:00:00Z",
            "timeMax": str(currentYear + 1) + "-08-01T00:00:00Z"
        }

        # Using google's python library for Google Cal API
        calendar_service = build(
            'calendar', 'v3', developerKey=GOOGLE_API_KEY)

        # have to include following comment otherwise error (google's fault not mine)
        # pylint: disable=no-member
        academic_events = calendar_service.events().list(
            calendarId=OPTIONS["calendarId"],
            orderBy=OPTIONS["orderBy"],
            singleEvents=True,
            timeMin=OPTIONS["timeMin"],
            timeMax=OPTIONS["timeMax"]).execute()

        # academic events storage object
        eventsList = {
            "last_fetched": datetime.datetime.now().isoformat(),
            "events": [],
            "error": False
        }

        # cleaing up data from the response and adding to storage dict
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
