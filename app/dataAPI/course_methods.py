import requests
import json
from app.dataAPI.academic_cal import getAcademicCalendarInfo, getImportantEvents
from dateutil.rrule import rrule, WEEKLY
from dateutil.parser import parse as datetimeparser
import datetime

BASE_URL = "https://classy.thecorp.org/search-submit/"  # Base url for classy API
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
}  # Base options to be included on class request


def get_course_info(values):
    """Get all course info EXCEPT for timings

    Args:
        values (dict): dict from front-end request containing search params

    Returns:
        dict: returns classes that match the search params
    """

    # Create payload to send to classy
    data = BASE_OPTIONS.copy()
    data["crn"] = values['crn']
    data['class_name'] = values['class_name']
    data['prof_name'] = values['prof_name']
    data['department'] = values['dep_name']

    try:
        # Make request
        response = requests.post(BASE_URL, data=data)
        return response.json()
    except Exception as e:

        # Error? Return error, message, and full response
        return {"error": True, "message": e, "response": response}


def get_course_timing_info(crn):
    """Gets the course timings information using CRN of course

    Args:
        crn (string): CRN of course

    Returns:
        dict: dict containing timing information
    """

    try:
        # Init result request
        result = {"error": False}
        response = requests.get(
            "https://classy.thecorp.org/get-event-source/" +
            str(crn))
        # sending json not supported by classy servers
        result["data"] = json.loads(response.text)

        return result
    except Exception as e:

        # Error? Return error, message, and full response
        return {"error": True, "message": e, "response": response}


def get_all_course_info(values):
    """Makes the requests needed to get all course info

    Args:
        values (dict): Dict with values passed from front-end form

    Returns:
        dict: contains results of search will ALL information
    """

    info = get_course_info(values)

    # Usually occurs if a class does not exist
    if info["error"]:
        return info

    # Update timing information for each session
    for result in info['results']:
        result['timings'] = processDate(
            get_course_timing_info(result["crn"])["data"])

    return json.dumps(info)


def processDate(timings):
    """Processes dates so that they accurately reflect start dates of classes

    Args:
        timings (List: session_info): list of sessions where a course occurs

    Returns:
        List: session_info: returns session_info dict with updated timing information
    """

    important_dates = getImportantEvents()
    result = timings

    # figure out what semester it is
    now = datetime.datetime.now().timestamp()
    compare = []
    curr_sem = "N"  # stands for neither

    for sem in important_dates['periods'].keys():
        processed = datetimeparser(
            important_dates['periods'][sem]['start']['start']['datetime'])
        compare.append({
            "value": abs(processed.timestamp() - now),
            "name": sem
        })

    if(compare[0]['value'] > compare[1]['value']):
        curr_sem = compare[1]['name']
    else:
        curr_sem = compare[0]['name']

    current_important_dates = important_dates['periods'][curr_sem]

    # Processing timings so that they reflect the current semester
    for instance in result:

        # Get next semester's start date
        gen_start_date = datetimeparser(
            current_important_dates["start"]["start"]["datetime"])

        # Get next semester's end date
        gen_end_date = datetimeparser(
            current_important_dates["end"]["start"]["datetime"])

        # Get the weekday that the session starts on
        weekdayNo = datetimeparser(instance['start']).weekday()

        # Get start time and turn it into list (acts as as tuple)
        start = datetimeparser(instance['start']).time(
        ).isoformat().split(".")[0].split(":")

        # Get end time and turn it into a list (acts as a tuple)
        end = datetimeparser(instance['end']).time(
        ).isoformat().split(".")[0].split(":")

        # Get weekday number that the semester starts on
        startWeekdayNumber = gen_start_date.weekday()

        # Figure out first date by going to the day semester starts
        # and moving back to the first day of the week
        firstWeekStart = gen_start_date - \
            datetime.timedelta(days=startWeekdayNumber)

        # Then, move forward to the date of the actual session
        gen_start_time = firstWeekStart + \
            datetime.timedelta(days=weekdayNo)

        # Adjust the end datetime as well to be on this day
        gen_end_time = firstWeekStart + datetime.timedelta(days=weekdayNo)

        # Add the timing component to the first date of the session
        gen_start_time = gen_start_time.replace(
            hour=int(start[0]), minute=int(start[1]))
        gen_end_time = gen_end_time.replace(
            hour=int(end[0]), minute=int(end[1]))

        # Convert to ISO string for consistency between frontend and backend
        instance['start'] = gen_start_time.isoformat()
        instance['end'] = gen_end_time.isoformat()

        # add rref rule to event to generate subsequent events
        rrule1 = rrule(
            until=gen_end_date,
            freq=WEEKLY,
            dtstart=gen_start_time)

        # add rule to the object
        instance['rrule'] = str(rrule1)

        # add duration of session (used in frontend)
        duration = gen_end_time - gen_start_time
        duration = str(duration)

        # Change duration to hours and mins format (used in frontend)
        instance['duration'] = ":".join(duration.split(":")[0:2])

    return result
