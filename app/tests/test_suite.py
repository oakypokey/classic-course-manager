import json
import os
from os import listdir
from os.path import isfile, join
import pytest
from app.dataAPI.academic_cal import (getAcademicCalendarInfo,
                                      makeAcademicCalApiCall, readFromFile,
                                      writeToFile, getImportantEvents)
from app.dataAPI.course_methods import get_all_course_info

CI_ENV = os.environ.get("CI") == "true"

# ~~~ Academic Calendar ~~~

# Make a new request as a fixture
@pytest.mark.skipif(
    CI_ENV == True, reason="to avoid making requests on CI server that require auth")
@pytest.fixture
def academic_cal_info():
    info = makeAcademicCalApiCall()
    return info

# Pass in fixture and test contents
@pytest.mark.skipif(
    CI_ENV == True, reason="to avoid making requests on CI server that require auth")
def test_academic_cal_response_contents(academic_cal_info):
    assert not academic_cal_info["error"]
    assert "events" in academic_cal_info
    assert len(academic_cal_info["events"]) > 0

# Save fixture to a pickle
@pytest.mark.skipif(
    CI_ENV == True, reason="to avoid making requests on CI server that require auth")
def test_pickling_academic_cal_response(academic_cal_info):
    fileName = "academic_cal_test.pickle"  # test file name

    # write to file
    result = writeToFile(
        academic_cal_info, fileName=fileName)
    assert result

    # Check if file exists
    dataPath = os.path.join(os.path.dirname(__file__), "..", "..")

    outputFiles = [output for output in listdir(
        dataPath) if isfile(join(dataPath, output))]

    assert fileName in outputFiles

# Read fixture from pickle and compare to fixture
@pytest.mark.skipif(
    CI_ENV == True, reason="to avoid making requests on CI server that require auth")
def test_unpickling_academic_cal_response(academic_cal_info):
    fileName = "academic_cal_test.pickle"
    filePath = os.path.join(os.path.dirname(__file__), "..", "..", fileName)
    file_contents = readFromFile(fileName=fileName)

    assert not file_contents["error"]
    assert "events" in file_contents
    assert len(file_contents["events"]) > 0

    os.remove(filePath)

# Important events function returns correct events


@pytest.mark.skipif(
    CI_ENV == True, reason="to avoid making requests on CI server that require auth")
def test_get_important_events():
    important_events = getImportantEvents()
    assert 'important_events' in important_events
    assert 'holidays' in important_events
    assert 'periods' in important_events
    assert len(important_events["important_events"]) > 0
    assert len(important_events["holidays"]) > 0
    assert len(important_events["periods"]) == 2

# ~~~Classy Methods~~~

# Make a request as a fixture for a basket of events
@pytest.mark.skipif(
    CI_ENV == True, reason="to avoid making requests on CI server that require auth")
@pytest.fixture
def course_basket_info():
    sample_search = {
        'crn': "",
        'class_name': "Accounting I",
        'prof_name': "",
        'dep_name': ""
    }

    info = get_all_course_info(sample_search)
    return json.loads(info)

# Make a request as a fixture for a class that does not exist
@pytest.fixture
def course_basket_failed_info():
    sample_search = {
        'crn': "12345",
        'class_name': "",
        'prof_name': "",
        'dep_name': ""
    }

    info = get_all_course_info(sample_search)
    return info

# Check that the dates are within the next year
@pytest.mark.skipif(
    CI_ENV == True, reason="to avoid making requests on CI server that require auth")
def test_good_basket(course_basket_info):
    assert not course_basket_info["error"]
    assert "results" in course_basket_info
    assert len(course_basket_info["results"]) > 0
    assert "sname" in course_basket_info["results"][0]
    assert "professor__name" in course_basket_info["results"][0]
    assert "timings" in course_basket_info["results"][0]
    assert len(course_basket_info["results"][0]["timings"]) > 0

# Check that an error is thrown


def test_bad_basket(course_basket_failed_info):
    assert "error" in course_basket_failed_info
    assert course_basket_failed_info["error"]
