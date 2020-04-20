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
GOOGLE_API_KEY=os.environ.get("GOOGLE_API_KEY")

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

    age = datetime.datetime.now().timestamp() - datetimeparse(response['last_fetched']).timestamp()
    print(age)
    if (age > (60 * 60 * 23)): #update every 24 hours lol
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

    calendar_service = build('calendar', 'v3', developerKey=GOOGLE_API_KEY)

    # pylint: disable=no-member
    academic_events = calendar_service.events().list(calendarId=OPTIONS["calendarId"], orderBy=OPTIONS["orderBy"], singleEvents=True, timeMin=OPTIONS["timeMin"], timeMax=OPTIONS["timeMax"]).execute()

    # TODO: Process this data so that it can be accepted by front-end
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



    