import datetime
import json

import requests
from dateutil.parser import parse as datetimeparse

from app.dataAPI.academic_cal import getImportantEvents


def get_user_calendar_book(access_token):
    blacklist = ["georgetown.edu_5bdj87g8237emjmvigu4rak1is@group.calendar.google.com",
                 "addressbook#contacts@group.v.calendar.google.com"]
    headers = headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(
        "https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)
    result = response.json()
    print(result)

    if 'error' in result:
        return result

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
    headers = {"Authorization": "Bearer " + access_token}
    params = {
        "timeMin": str(datetime.datetime.now().year) + "-08-01T00:00:00.000Z",
        "timeMax": str(datetime.datetime.now().year + 1) + "-08-01T00:00:00.000Z",
        "singleEvents": True,
        "orderBy": "startTime"
    }

    response = requests.get("https://www.googleapis.com/calendar/v3/calendars/" +
                            calendar_id + "/events", headers=headers, params=params)

    processed = response.json()

    return processed


def insert_user_calendar_events(access_token, calendar_id, events_array):
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
        'recurrance': [],
        'source': {
            "title": "Classic Course Manager",
            "url": "https://classic-course-manager.herokuapp.com"
        },
        "description": "Class idk"
    }

    responses = []

    # eventually this will go over every event in the basket
    for event in events_array:
        processed_event_data_stub = processed_event_data_template
        processed_event_data_stub['summary'] = event['courseName']
        processed_event_data_stub['description'] = event['subjectName'] + " - " + \
            event['section'] + " with Professor " + \
            event['professorName'] + " | CRN: " + event['crn']

        for course_session in event['timings']:
            processed_event_data = processed_event_data_stub
            processed_event_data['recurrence'] = [
                course_session['rrule'].split("\n")[1] + "Z"]
            processed_event_data['start']['dateTime'] = course_session['start']
            processed_event_data['end']['dateTime'] = course_session['end']

            export = json.dumps(processed_event_data)
            print(export, "\n")
            response = requests.post("https://www.googleapis.com/calendar/v3/calendars/" +
                                     calendar_id + "/events", headers=headers, data=json.dumps(processed_event_data))
            print(response.json())
            responses.append(response.json())

    return responses


def clean_recurrences(access_token, calendar_id, full_clean_flag):
    importantEvents = getImportantEvents()

    response = get_classic_generated_events(access_token, calendar_id)

    instance_dict = {}

    for event in response:
        instance_dict[event["id"]] = get_instances_from_event_id(
            access_token, calendar_id, event["id"])

    # collect ids of instances that need to be removed from each event
    removal_ids = []

    def removal_id_filter(instance):
        test = datetimeparse(
            instance['start']['dateTime']).replace(tzinfo=None)
        flag = True

        fall_start = datetimeparse(
            importantEvents['periods']['fall_semester']["start"]["start"]["datetime"]).replace(tzinfo=None)
        fall_end = datetimeparse(
            importantEvents['periods']['fall_semester']["end"]["start"]["datetime"]).replace(tzinfo=None)

        spring_start = datetimeparse(
            importantEvents['periods']['spring_semester']["start"]["start"]["datetime"]).replace(tzinfo=None)
        spring_end = datetimeparse(
            importantEvents['periods']['spring_semester']["end"]["start"]["datetime"]).replace(tzinfo=None)

        #print(test, fall_start)
        # class occurs in fall semester
        if test > fall_start and test < fall_end:
            flag = False
            #print("in the fall")

        # before spring semester begins
        if test > spring_start and test < spring_end:
            flag = False
            #print("in the spring")

        # is on any blacklisted dates
        for holiday in importantEvents['holidays']:
            if test.date() == datetimeparse(holiday).date() and not flag:
                flag = True
                #print("not a holiday")

        return flag

    for event_id in instance_dict.keys():
        result = filter(
            removal_id_filter,
            instance_dict[event_id]['items'])
        result = list(result)
        for instance in result:
            removal_ids.append(instance['id'])

    # print(removal_ids)

    return {"body": removal_ids}


def get_instances_from_event_id(access_token, calendar_id, event_id):
    headers = {"Authorization": "Bearer " +
               access_token, "Accept": "application/json"}
    response = requests.get("https://www.googleapis.com/calendar/v3/calendars/" +
                            calendar_id + "/events/" + event_id + "/instances", headers=headers)

    try:
        return response.json()
    except Exception as e:
        return {"error": True, "message": e}


def clear_all_classic_events(access_token, calendar_id, event_id_array):
    responses = []

    for event_id in event_id_array:
        responses.append(clear_classic_event(
            access_token, calendar_id, event_id))

    return responses


def get_classic_generated_events(access_token, calendar_id):
    importantEvents = getImportantEvents()

    headers = {"Authorization": "Bearer " +
               access_token, "Accept": "application/json"}
    params = {
        "timeMin": importantEvents['periods']['fall_semester']['start']['start']['datetime'] + "T00:00:00.000Z",
        "timeMax": importantEvents['periods']['spring_semester']['end']['start']['datetime'] + "T00:00:00.000Z",
        "singleEvents": False
    }

    response = requests.get("https://www.googleapis.com/calendar/v3/calendars/" +
                            calendar_id + "/events", headers=headers, params=params)

    try:
        response = response.json()
        response = response['items']
    except BaseException:
        return response

    def filterFunc(event):
        if 'source' not in event:
            return False
        return event['source']['title'] == 'Classic Course Manager'

    response = filter(filterFunc, response)

    return list(response)


def clear_classic_event(access_token, calendar_id, event_id):
    headers = {"Authorization": "Bearer " +
               access_token, "Accept": "application/json"}
    response = requests.delete("https://www.googleapis.com/calendar/v3/calendars/" +
                               calendar_id + "/events/" + event_id, headers=headers)
    try:
        return response.json()
    except Exception as e:
        return {"error": True, "message": e}
