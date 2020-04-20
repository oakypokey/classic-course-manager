import requests
import json
import datetime

def get_user_calendar_book(access_token):
    blacklist = ["georgetown.edu_5bdj87g8237emjmvigu4rak1is@group.calendar.google.com", "addressbook#contacts@group.v.calendar.google.com"]
    headers = headers = {"Authorization": "Bearer " + access_token}
    response = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)

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