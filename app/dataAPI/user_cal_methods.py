import datetime
import json

import requests
from dateutil.parser import parse as datetimeparse
from app.dataAPI.academic_cal import getImportantEvents


def get_user_calendar_book(access_token):
    """Get the logged on user's list of calendars

    Args:
        access_token (string): the access token used to make the request

    Returns:
        List: A list with all user calendars and their attributes
    """

    # Do not want academic calendar or contacts events
    blacklist = ["georgetown.edu_5bdj87g8237emjmvigu4rak1is@group.calendar.google.com",
                 "addressbook#contacts@group.v.calendar.google.com"]

    # Create headers for request
    headers = headers = {"Authorization": "Bearer " + access_token}

    try:
        # Make request for for the list of calendars
        response = requests.get(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)

        result = response.json()

        if 'error' in result:
            return result

    except Exception as e:
        # Error? Return error, message, and full response
        return {"error": True, "message": e, "response": response}

    # Create old state
    processed = result["items"]

    # Where updated state will be stored
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
    """Gets the events of a particular users calendar from Google Cal API

    Args:
        access_token (string): Access token used to make the request to gcal API
        calendar_id (string): ID for the specifc user calendar to get events from

    Returns:
        Dict: Dictionary following response conventions of Google Calendar API. attr 'items' contains events array
    """

    # Create the headers for the request
    headers = {
        "Authorization": "Bearer " + access_token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Create the params object for the request
    params = {
        "timeMin": str(datetime.datetime.now().year) + "-08-01T00:00:00.000Z",
        "timeMax": str(datetime.datetime.now().year + 1) + "-08-01T00:00:00.000Z",
        "singleEvents": True,
        "orderBy": "startTime"
    }

    try:
        # Make request
        response = requests.get("https://www.googleapis.com/calendar/v3/calendars/" +
                                calendar_id + "/events", headers=headers, params=params)

        # Try to process
        processed = response.json()

        return processed

    except Exception as e:
        # Error? Return error, message, and full response
        return {"error": True, "message": e, "response": response}


def insert_user_calendar_events(access_token, calendar_id, events_array):
    """Inserts array of calendar objects into specific user gcal

    Args:
        access_token (string): User's access token to make the request
        calendar_id (string): ID of the specific user calendar to add events to
        events_array (dict[]): Array of event dictionaries that contain the event info

    Returns:
        List: List of response dicts to indicate the success of each insert request
    """

    # Create the headers to make the request
    headers = headers = {
        "Authorization": "Bearer " + access_token,
        "Accept": "application/json",
        "Content-Type": "application/json"}

    # Create a generic template so that if there is missing info it is filled
    # in already
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

    # Init response list so that we return nothing if we get nothing
    responses = []

    # Iterate over event object and create request payload for each
    for event in events_array:
        processed_event_data_stub = processed_event_data_template
        processed_event_data_stub['summary'] = event['courseName']
        processed_event_data_stub['description'] = event['subjectName'] + " - " + \
            event['section'] + " with Professor " + \
            event['professorName'] + " | CRN: " + event['crn']

        # Iterate over the course timings for each course to create a recurring
        # event for each
        for course_session in event['timings']:
            processed_event_data = processed_event_data_stub
            processed_event_data['recurrence'] = [
                course_session['rrule'].split("\n")[1] + "Z"]
            processed_event_data['start']['dateTime'] = course_session['start']
            processed_event_data['end']['dateTime'] = course_session['end']

            export = json.dumps(processed_event_data)

            # Make request and attempt to store
            try:
                response = requests.post("https://www.googleapis.com/calendar/v3/calendars/" +
                                         calendar_id + "/events", headers=headers, data=export)

                response_processed = response.json()

                responses.append(response_processed)

            except Exception as e:
                # Error? Store error, message, and full response
                response.append(
                    {"error": True, "message": e, "response": response})

    # Return the status of each of the responses
    return responses


def clean_recurrences(access_token, calendar_id, full_clean_flag=False):
    """Cleans up the instances of recurring events that occur on holidays

    Args:
        access_token (string): User's access token to make the request
        calendar_id (string): ID of the specific user calendar to remove events from
        full_clean_flag (bool): When True, removes all events created by classic from selected calendar

    Returns:
        Dict: Information about which instances are being removed and whether or not they were successful
    """

    # Get important events from the academic calendar
    importantEvents = getImportantEvents()

    # Get list of events that have been generated by classic
    # Get JSON out of response
    try:
        response = get_classic_generated_events(access_token, calendar_id)
    except Exception as e:
        return {"error": True, "message": e, "response": response}

    # Create a place to store all the information about each instance
    instance_dict = {}

    # Get the instances and then store them in the above object
    for event in response:
        instance_dict[event["id"]] = get_instances_from_event_id(
            access_token, calendar_id, event["id"])

    # Init list where IDs of events that need to be removed will be stored
    removal_ids = []

    def removal_id_filter(instance):
        """Filter function to determine which classic event instances need to be removed

        Args:
            instance (event: Dict): a specific instance of a recurring event from Google Cal API response

        Returns:
            bool: whether or not the date should be kept of removed. Follows in-built filter conventions
        """

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

        # class occurs in fall semester
        if test > fall_start and test < fall_end:
            flag = False

        # before spring semester begins
        if test > spring_start and test < spring_end:
            flag = False

        # is on any blacklisted dates
        for holiday in importantEvents['holidays']:
            if test.date() == datetimeparse(holiday).date() and not flag:
                flag = True

        return flag

    # Go over classic generated events and check their instances
    for event_id in instance_dict.keys():
        result = filter(
            removal_id_filter,
            instance_dict[event_id]['items'])  # returns list of instances that need to be removed
        result = list(result)                  # for the recurring event
        for instance in result:
            # take the ids and add them to main list
            print(instance)
            removal_ids.append(instance['id'])

    # TODO: Actually implement clean events

    clear_response = clear_multiple_classic_events(
        access_token, calendar_id, removal_ids)

    errFlag = False
    for status in clear_response:
        if status['error']:
            errFlag = True

    success_events = []
    if not errFlag:
        for key in instance_dict.keys():
            success_events.append(instance_dict[key]["items"][0])

    return {"body": success_events}


def get_instances_from_event_id(access_token, calendar_id, event_id):
    """Simple function to get instances of a recurring event from Google Calendar API

    Args:
        access_token (string): User's access token to make the request
        calendar_id (string): ID of the specific calendar that the event exists on
        event_id (string): ID of the recurring event to get the instances of

    Returns:
        Dict: Returns the normal response to the '/instances' endpoint as outlined in Google Cal API reference
    """
    # Headers for the request
    headers = {"Authorization": "Bearer " +
               access_token, "Accept": "application/json"}

    # Make the request
    response = requests.get("https://www.googleapis.com/calendar/v3/calendars/" +
                            calendar_id + "/events/" + event_id + "/instances", headers=headers)

    try:
        # Attempt to get JSON
        return response.json()
    except Exception as e:
        # Otherwise return an error occured with info + response
        return {"error": True, "message": e, "response": response}


def clear_multiple_classic_events(access_token, calendar_id, event_id_array):
    """Simple function to handle clearing an array of classic events

    Args:
        access_token (string): User's access token to make the request
        calendar_id (string): ID of the specific calendar that the events exist on
        event_id_array (string[]): list of event ID strings to clear

    Returns:
        List: List of dicts that contain response information
    """
    # Init responses list
    responses = []

    # Return empty list if an empty list is given
    if not len(event_id_array) > 0:
        return responses

    # Go through given list and make requests
    for event_id in event_id_array:
        response = clear_classic_event(
            access_token, calendar_id, event_id)

        responses.append(response)  # store in responses list

    return responses


def get_classic_generated_events(access_token, calendar_id):
    """Gets a list of classic generated events

    Args:
        access_token (string): User's access token to make the request
        calendar_id (string): ID of the specific calendar that the event exists on

    Returns:
        List: list of events that were generated by classic in the calendar
    """

    # Get important events to help infrom request params
    importantEvents = getImportantEvents()

    # Create headers for request
    headers = {"Authorization": "Bearer " +
               access_token, "Accept": "application/json"}
    params = {
        # Only get events for this year
        "timeMin": importantEvents['periods']['fall_semester']['start']['start']['datetime'] + "T00:00:00.000Z",
        "timeMax": importantEvents['periods']['spring_semester']['end']['start']['datetime'] + "T00:00:00.000Z",
        "singleEvents": False  # Classic events are recurring
    }

    # Make request
    response = requests.get("https://www.googleapis.com/calendar/v3/calendars/" +
                            calendar_id + "/events", headers=headers, params=params)

    # Simple function that checks the source attribute of events to see
    # if they are Classic events
    def filterFunc(event):
        if 'source' not in event:
            return False
        return event['source']['title'] == 'Classic Course Manager'

    try:
        responseProcessed = response.json()  # try to get response json
        # get all the events in the calendar
        responseProcessed = responseProcessed['items']
        # filter to get Classic events
        responseProcessed = filter(filterFunc, responseProcessed)

    except BaseException:
        return response  # problem? return the full response

    return list(responseProcessed)  # return list of classic generated events


def clear_classic_event(access_token, calendar_id, event_id):
    """Clears a single classic event

    Args:
        access_token (string): User's access token to make the request
        calendar_id (string): ID of the specific calendar that the event exists on
        event_id (string): ID fo the event to remove

    Returns:
        Dict: Dict that follows Google Calendar API response to delete method of events endpoint
    """

    # Set headers for the request
    headers = {"Authorization": "Bearer " +
               access_token, "Accept": "application/json"}

    # Make request
    response = requests.delete("https://www.googleapis.com/calendar/v3/calendars/" +
                               calendar_id + "/events/" + event_id, headers=headers)

    try:
        # Return response JSON
        return {"error": response.status_code != 204, "event_id": event_id}
    except Exception as e:
        # Error? Return error, message, and the full response
        return {"error": True, "message": e, "response": response}
