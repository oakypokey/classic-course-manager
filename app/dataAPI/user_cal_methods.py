import requests
import json
import datetime
from dateutil.parser import parse as datetimeparse

def get_user_calendar_book(access_token):
    blacklist = ["georgetown.edu_5bdj87g8237emjmvigu4rak1is@group.calendar.google.com", "addressbook#contacts@group.v.calendar.google.com"]
    headers = headers = {"Authorization": "Bearer " + access_token}
    response = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)

    print(response.json())

    processed = response.json()["items"]
    final = []

    for item in processed:
        if item["id"] not in blacklist:
            processedItem = {
            "id": item["id"],
            "title": item["summary"],
            "color": item["backgroundColor"],
            }

            if 'primary' in item.keys():
                processedItem['primary'] = True
            else:
                processedItem['primary'] = False

            if 'selected' in item.keys():
                processedItem["selected"] = True
            else:
                processedItem["selected"] = False

            final.append(processedItem)

    return final

def get_user_calendar_events(access_token, calendar_id):
    headers = headers = {"Authorization": "Bearer " + access_token}
    params = {
        "timeMin": str(datetime.datetime.now().year) + "-08-01T00:00:00.000Z",
        "timeMax": str(datetime.datetime.now().year + 1) + "-08-01T00:00:00.000Z",
        "singleEvents": True,
        "orderBy": "startTime"
    }

    response = requests.get("https://www.googleapis.com/calendar/v3/calendars/"+ calendar_id + "/events", headers=headers, params=params)

    processed = response.json()

    return processed

def insert_user_calendar_events(access_token, calendar, events_array):
    headers = headers = {
        "Authorization": "Bearer " + access_token,
        "Accept": "application/json",
        "Content-Type": "application/json"}

    processed_event_data_template = {
        'end': {
            'dateTime': '2020-04-20T15:00:00',
            'timeZone': 'America/New_York'
        },
        'start': {
            'dateTime': '2020-04-20T13:00:00',
            'timeZone': 'America/New_York'
        },
        'summary': "Example event",
        #'recurrance': [], #RRULE goes here
        'source': {
            "title": "Classic Course Manager",
            "url": "https://classic-course-manager.herokuapp.com"
        },
        "description": "Class idk"
    }

    responses = []

    # eventually this will go over every event in the basket
    for event in events_array:
        processed_event_data = processed_event_data_template

        processed_event_data = json.dumps(processed_event_data)
        response = requests.post("https://www.googleapis.com/calendar/v3/calendars/"+ calendar["id"] + "/events", headers=headers, data=processed_event_data)
        print(response.json())
        responses.append(response.json())

    return responses
