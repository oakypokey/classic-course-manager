import React, {
  useState,
  FormEventHandler,
  CSSProperties,
  useEffect,
} from "react";
import logo from "./logo.svg";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { Navigation } from "./components/Navigation";
import {
  CourseCard,
  CourseCardProps,
  CourseTimings,
} from "./components/CourseCard";

import { CourseSearch, FormValues } from "./components/CourseSearch";

import {
  Container,
  Row,
  Col,
  Button,
  Navbar,
  NavbarBrand,
  NavbarText,
  NavbarToggler,
  Nav,
  InputGroup,
  InputGroupAddon,
  InputGroupText,
  Input,
  Carousel,
  UncontrolledAlert,
  Dropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  UncontrolledDropdown,
  Spinner,
  Badge,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Label,
} from "reactstrap";
import { CalendarSection, EventProperties } from "./components/CalendarSection";
import { URLSearchParams } from "url";
import { timeAsMs } from "@fullcalendar/core/datelib/marker";
import { formatIsoTimeString } from "@fullcalendar/core";
import { InformationModal } from "./components/InformationModal";

const COLORS = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"];
interface APIResponse {
  error: boolean;
  results: APIResponseCourse[];
  message?: string;
}

interface APIResponseCourse {
  crn: number;
  level: string;
  multiple_sections: boolean;
  name: string;
  professor__name: string;
  remaining: number;
  section: string;
  show_xlist: boolean;
  sname: string;
  waitlistact: number;
  timings: APIResponseTimingsData[];
  message?: string;
}

interface APIResponseTimingsData {
  allDay: boolean;
  end: string;
  start: string;
  title: string;
  crn: number;
  id: number;
  rrule: string;
  duration: string;
}

interface AcademicCalEventProperties {
  start: AcademicCalDateProperties;
  end: AcademicCalDateProperties;
  summary: string;
  description: string;
}

interface AcademicCalDateProperties {
  date?: string;
  dateTime?: string;
  timeZone?: string;
}

interface AcademicCalEventsResponseProperties {
  last_fetched: string;
  events: AcademicCalEventProperties[];
  error: boolean;
  message?: string;
}

export interface SessionUserData {
  email: string;
  email_verified: boolean;
  family_name: string;
  given_name: string;
  locale: string;
  name: string;
  nickname: string;
  picture: string;
  sub: string;
  updated_at: string;
  calendar_book?: UserCalendarBookItem[];
}

export interface UserCalendarBookItem {
  id: string;
  title: string;
  color: string;
  primary: boolean;
  selected: boolean;
}

const defaultUserCalendarBookItem = {
  id: "",
  title: "Select a calendar",
  color: "#f0f0f0",
  primary: false,
  selected: false,
};

function App() {
  const [inputCRN, setInputCRN] = useState("");
  const [basket, setBasket] = useState([] as CourseCardProps[]);
  const [search, setSearch] = useState([] as CourseCardProps[]);
  const [requestError, setRequestError] = useState(false);
  const [academicCalEvents, setAcademicCalEvents] = useState(
    [] as EventProperties[]
  );
  const [userData, setUserData] = useState({} as SessionUserData);
  const [selectedCalendar, setSelectedCalendar] = useState(
    defaultUserCalendarBookItem as UserCalendarBookItem
  );
  const [loading, setLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [message, setMessage] = useState("");

  const [modal, setModal] = useState(false);
  const [execute, setExecute] = useState(false);

  const [aboutModal, setAboutModal] = useState(false);
  const [helpModal, setHelpModal] = useState(false);

  const toggleAbout = () => setAboutModal(!aboutModal);
  const toggleHelp = () => setHelpModal(!helpModal);

  const toggle = () => setModal(!modal);

  const valuesDefault = {
    dep_name: "",
    crn: "",
    prof_name: "",
    class_name: "",
  } as FormValues;

  const [values, setValues] = useState(valuesDefault);

  //Just like component did mount <3
  useEffect(() => {
    fetch("/api/getacademiccalinfo")
      .then((res) => res.json())
      .then((response: AcademicCalEventsResponseProperties) => {
        let AcademicCalEventsProcessed = [] as EventProperties[];
        if (response.error) {
          console.log("Error when fetching response: " + response.message);
          return;
        }

        AcademicCalEventsProcessed = response.events.map((event) => {
          let startTime = new Date();
          let endTime = new Date();

          if (event.start.date && event.end.date) {
            startTime = new Date(Date.parse(event.start.date));
            startTime = new Date(Date.parse(event.end.date));
          } else if (event.start.dateTime && event.end.dateTime) {
            startTime = new Date(Date.parse(event.start.dateTime));
            endTime = new Date(Date.parse(event.end.dateTime));
          }

          const allDayBool =
            startTime.getTime() - endTime.getTime() > 1000 * 60 * 60 * 23;
          return {
            start: startTime,
            end: endTime,
            title: event.summary,
            allDay: allDayBool,
          } as EventProperties;
        });
        setAcademicCalEvents(AcademicCalEventsProcessed);

        fetch("/api/user_data")
          .then((res) => res.json())
          .then((data) => {
            let userCalBook = data.user_calendar_book;
            userCalBook.sort(
              (cal_a: UserCalendarBookItem, cal_b: UserCalendarBookItem) => {
                return cal_a.selected === cal_b.selected
                  ? 0
                  : cal_a.selected
                  ? -1
                  : 1;
              }
            );
            const userData = {
              ...data.session,
              calendar_book: userCalBook,
            };
            setUserData(userData as SessionUserData);
          });
      });
  }, []);

  useEffect(() => {
    if (userData.calendar_book) {
      const primaryCal = userData.calendar_book.filter((cal) => {
        return cal.primary;
      })[0];
      setSelectedCalendar(primaryCal);
    }
  }, [userData]);

  const randomColor = (() => {
    "use strict";

    const randomInt = (min: number, max: number) => {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    };

    return () => {
      var h = randomInt(0, 360);
      var s = randomInt(42, 98);
      var l = randomInt(40, 90);
      return `hsl(${h},${s}%,${l}%)`;
    };
  })();

  const handleSubmit = (e: React.FormEvent, values: FormValues) => {
    e.preventDefault();
    setRequestError(false);
    setLoading(true);
    setSearch([]);
    if (
      basket.filter((course) => {
        return course.crn == inputCRN;
      }).length < 1
    ) {
      fetch("/api/getinfo", {
        method: "POST",
        body: JSON.stringify(values),
        headers: { "Content-Type": "application/json" },
      })
        .then((res: Response) => {
          try {
            let result: Promise<APIResponse> = res.json();
            return result;
          } catch (err) {
            console.log(err);
            throw err;
          }
        })
        .then((result) => {
          if (result.error) {
            throw new Error(result.message);
          }
          console.log(result);
          return result;
        })
        .then((response) => {
          const courseCards = response.results.map(
            (result: APIResponseCourse) => {
              let processedResponse: CourseCardProps | null = null;
              let processedResponseTimings: CourseTimings[] = result.timings.map(
                (timing) => {
                  return {
                    weekday: new Date(timing.start).getDay(),
                    start: new Date(timing.start),
                    end: new Date(timing.end),
                    rrule: timing.rrule,
                    duration: timing.duration,
                  };
                }
              );

              return {
                courseName: result.name,
                subjectName: result.sname,
                section: result.section,
                professorName: result.professor__name,
                crn: result.crn.toString(),
                timings: processedResponseTimings,
                color: randomColor(),
              } as CourseCardProps;
            }
          );

          console.log(JSON.stringify(courseCards));

          setSearch(courseCards);
        })
        .catch((err: Error) => {
          setRequestError(true);
          console.log("OOOO", err);
        })
        .finally(() => {
          setValues(valuesDefault);
          setLoading(false);
        });
    } else {
      setRequestError(true);
    }
  };

  const handleRemoveButtonClick = (crn: string) => {
    let newState = basket;
    newState = newState.filter((course) => {
      if (course.crn === crn) {
        setSearch([...search, course]);
      }
      return course.crn !== crn;
    });
    console.log(newState);
    setBasket(newState);
  };

  const handleAddButtonClick = (crn: string) => {
    //remove from search bar
    setSearch(
      search.filter((course) => {
        return course.crn !== crn;
      })
    );

    //add to basket
    const newClass = search.filter((course) => {
      return course.crn === crn;
    });
    setBasket([...basket, ...newClass]);
  };

  const sectionStyle: CSSProperties = {
    borderColor: "grey", //"#a6e3e9",
    borderWidth: "2px",
    borderStyle: "solid",
    height: "80vh",
    //backgroundColor: "#e3fdfd"
  };

  const getCalSelectStyle = (cal: UserCalendarBookItem) => {
    return {
      backgroundColor: cal.color,
    } as CSSProperties;
  };

  const handleCalendarExport = () => {
    setExportLoading(true);
    const payload = {
      basket: basket,
      calendar_id: selectedCalendar.id,
    };
    fetch("/api/user_events", {
      method: "POST",
      body: JSON.stringify(payload),
      headers: { "Content-Type": "application/json" },
    })
      .then((res) => res.json())
      .then((res) => {
        console.log(res);
        let messageString: string[] = res.body.map((event: any) => {
          return event.summary;
        });

        messageString = messageString.filter(
          (v, i) => messageString.indexOf(v) === i
        );
        const finalMessage =
          "The following classes are currently on your calendar:!" +
          messageString.join("!");
        setMessage(finalMessage);
        setExportLoading(false);
        setBasket([]);
      });
  };

  const handleClearEvents = () => {
    setExportLoading(true);
    fetch("/api/clear_events", {
      method: "POST",
      body: JSON.stringify({ calendar_id: selectedCalendar.id }),
      headers: { "Content-Type": "application/json" },
    })
      .then((res) => res.json())
      .then((res) => {
        console.log(res);
        setExportLoading(false);
        setMessage("All Classic Events were deleted successfully!");
      })
      .catch((e) => {
        console.log(e);
        setExportLoading(false);
        setMessage("An error occured");
      });
  };

  const handleExportButtonClick = () => {
    setExecute(true);
    setMessage("You are about to export your basket. Are you sure?");
    toggle();
  };

  const handleClearCalendarClick = () => {
    setExecute(false);
    setMessage(
      "Would you like to clear all Classic events for: " +
        selectedCalendar.title +
        "?"
    );
    toggle();
  };

  const deleteEventButton = {
    type: "danger",
    text: "Delete Events",
  };

  const exportButton = {
    type: "success",
    text: "Export classes",
  };

  const onClickAbout = () => {
    toggleAbout();
  };

  const onClickHelp = () => {
    toggleHelp();
  };

  return (
    <div className="App">
      <Navigation
        userData={userData}
        onClickAbout={onClickAbout}
        onClickHelp={onClickHelp}
      />
      {execute ? (
        <InformationModal
          modal={modal}
          toggle={toggle}
          setModal={setModal}
          execute={handleCalendarExport}
          loading={exportLoading}
          message={message}
          setMessage={setMessage}
          title={"Calendar Export"}
          buttonSettings={exportButton}
        />
      ) : (
        <InformationModal
          modal={modal}
          toggle={toggle}
          setModal={setModal}
          execute={handleClearEvents}
          loading={exportLoading}
          message={message}
          setMessage={setMessage}
          title={"Clear Classic Events"}
          buttonSettings={deleteEventButton}
        />
      )}

      {/* This is the about modal */}
      <Modal isOpen={aboutModal} toggle={toggleAbout}>
        <ModalHeader toggle={toggleAbout}>About</ModalHeader>
        <ModalBody>
          <h3>What is this?</h3>
          This application was created for OPIM 244. You can use this
          application to search for classes, plan your schedule, and export your
          courses to your google calendar. Classic is smart in the way that it
          is able to automatically detect holidays and breaks and will not add
          classes to those days.
          <h3>Disclaimer</h3>
          Classic is in Beta which means sometimes things may not work as
          intended. Classic does not store any information from your calendar.
          When you logout, your session data is deleted from the server and
          cannot be recovered. Classic will only remove events from your
          calendar that were created by Classic. Course information is sourced
          from a third party and may not be accurate.
        </ModalBody>
        <ModalFooter>
          <Button color="primary" onClick={toggleAbout}>
            Close
          </Button>
        </ModalFooter>
      </Modal>

      {/* This is the help modal */}
      <Modal isOpen={helpModal} toggle={toggleHelp}>
        <ModalHeader toggle={toggleHelp}>Help</ModalHeader>
        <ModalBody>
          <h3>Common Issues</h3>
          <ul>
            <li>
              If you are unable to see your photo or your list of calendars,
              please log out and then log back in
            </li>
            <li>
              Need to redo your schedule? Select the calendar where previous
              Classic events are stored and click "Clear Calendar" to remove all
              events generated by Classic
            </li>
            <li>
              Want to delete individual events? You can delete them from the
              Google Calendar App
            </li>
          </ul>
        </ModalBody>
        <ModalFooter>
          <Button color="primary" onClick={toggleHelp}>
            Close
          </Button>
        </ModalFooter>
      </Modal>

      <Container fluid>
        <Row>
          <Col xl={12}>
            <CourseSearch
              handleSubmit={handleSubmit}
              setValues={setValues}
              values={values}
              requestError={requestError}
            />
            {requestError ? (
              <UncontrolledAlert label={"errmsg"} color={"danger"}>
                There was an error. Please try again.
              </UncontrolledAlert>
            ) : (
              ""
            )}
          </Col>
        </Row>
        <Row>
          <Col xl={2} style={{ ...sectionStyle, overflowY: "auto" }}>
            {loading ? (
              <Spinner
                style={{ width: "8rem", height: "8rem", marginTop: "100%" }}
              />
            ) : (
              ""
            )}
            {search.map((course, index) => {
              //prevents showing ones we already have added
              let basketCRNs = basket.map((course) => course.crn);
              if (basketCRNs.includes(course.crn)) {
                return;
              }

              return (
                <CourseCard
                  key={index}
                  handleAddButtonClick={handleAddButtonClick}
                  {...course}
                />
              );
            })}
          </Col>
          <Col xl={2} style={{ ...sectionStyle, overflowY: "auto" }}>
            {basket.map((course, index) => {
              return (
                <CourseCard
                  key={index}
                  handleRemoveButtonClick={handleRemoveButtonClick}
                  basket={true}
                  {...course}
                />
              );
            })}
          </Col>
          <Col xl={6} style={sectionStyle}>
            <CalendarSection
              events={basket}
              academicCalEvents={academicCalEvents}
            />
          </Col>
          <Col xl={2} style={sectionStyle}>
            <br />
            <h4 style={{ textAlign: "left" }}> Calendar Selection </h4>
            <UncontrolledDropdown group size="md">
              <DropdownToggle style={getCalSelectStyle(selectedCalendar)} caret>
                {" "}
                {selectedCalendar.title}
              </DropdownToggle>
              <DropdownMenu>
                {userData.calendar_book?.map((cal, index) => {
                  const selected = cal.id == selectedCalendar.id;
                  return (
                    <DropdownItem
                      active={selected}
                      key={index}
                      onClick={() => setSelectedCalendar(cal)}
                    >
                      {cal.title}
                    </DropdownItem>
                  );
                })}
              </DropdownMenu>
            </UncontrolledDropdown>
            <br />
            <br />
            <h4 style={{ textAlign: "left" }}> Export </h4>
            <Button
              disabled={!(basket.length > 0)}
              onClick={handleExportButtonClick}
              color="primary"
            >
              Export to Calendar
            </Button>
            <br />
            <br />
            <h5 style={{ textAlign: "left" }}>
              {" "}
              Clear all Classic events from {selectedCalendar.title}{" "}
            </h5>
            <Button color="danger" onClick={handleClearCalendarClick}>
              Clear Calendar
            </Button>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
