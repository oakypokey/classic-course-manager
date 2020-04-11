from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import json

load_dotenv()
GOOGLE_API_KEY=os.environ.get("GOOGLE_API_KEY")


def getAcademicCalendarInfo():
    OPTIONS = {
      "calendarId": "georgetown.edu_5bdj87g8237emjmvigu4rak1is@group.calendar.google.com",
      "orderBy": "startTime",
      "singleEvents": "true",
      "timeMin": "2020-08-01T00:00:00Z",
      "timeMax": "2021-08-01T00:00:00Z"
    }

    calendar_service = build('calendar', 'v3', developerKey=GOOGLE_API_KEY)

    # pylint: disable=no-member
    academic_events = calendar_service.events().list(calendarId=OPTIONS["calendarId"], orderBy=OPTIONS["orderBy"], singleEvents=True, timeMin=OPTIONS["timeMin"], timeMax=OPTIONS["timeMax"]).execute()

    # TODO: Process this data so that it can be accepted by front-end
    return academic_events