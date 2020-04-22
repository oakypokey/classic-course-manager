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
} from "reactstrap";
import { CalendarSection, EventProperties } from "./components/CalendarSection";
import { URLSearchParams } from "url";

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
  calendar_book?: UserCalendarBookItem[]
}

export interface UserCalendarBookItem {
  id: string
  title: string
  color: string
  primary: boolean
  selected: boolean
}

const defaultUserCalendarBookItem = {
  id: "",
  title: "Select a calendar",
  color: "#f0f0f0",
  primary: false,
  selected: false
}

function App() {
  const [inputCRN, setInputCRN] = useState("");
  const [basket, setBasket] = useState([] as CourseCardProps[]);
  const [search, setSearch] = useState([] as CourseCardProps[])
  const [requestError, setRequestError] = useState(false);
  const [academicCalEvents, setAcademicCalEvents] = useState(
    [] as EventProperties[]
  );
  const [userData, setUserData] = useState({} as SessionUserData);
  const [selectedCalendar, setSelectedCalendar] = useState(defaultUserCalendarBookItem as UserCalendarBookItem)

  const valuesDefault = {
    dep_name: "",
    crn: "",
    prof_name: "",
    class_name:""
  } as FormValues

  const [values, setValues] = useState(valuesDefault)

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
            let userCalBook = data.user_calendar_book
            userCalBook.sort((cal_a: UserCalendarBookItem, cal_b: UserCalendarBookItem) => {
              return (cal_a.selected === cal_b.selected) ? 0 : cal_a.selected ? -1 : 1; 
            })
            const userData = {
              ...data.session,
              calendar_book: userCalBook
            }
            setUserData(userData as SessionUserData);
          });
      });
  }, []);

  useEffect(() => {
    if(userData.calendar_book){
      const primaryCal = userData.calendar_book.filter((cal) =>{
        return cal.primary
      })[0]
      setSelectedCalendar(primaryCal)
    }
  }, [userData])

  const handleSubmit = (e: React.FormEvent, values: FormValues) => {
    e.preventDefault();
    setRequestError(false);
    if (
      basket.filter((course) => {
        return course.crn == inputCRN;
      }).length < 1
    ) {
      fetch("/api/getinfo", {
        method: 'POST',
        body: JSON.stringify(values),
        headers: {"Content-Type": "application/json"}
      })
        .then((res: Response) => {
          try {
            let result: Promise<APIResponse> = res.json();
            return result;
          }
          catch(err) {
            console.log(err)
            throw err
          }
        })
        .then((result) => {
          if (result.error) {
            throw new Error(result.message);
          }
          console.log(result)
          return result;
        })
        .then((response) => {
          const courseCards = response.results.map((result: APIResponseCourse) => {
            let processedResponse: CourseCardProps | null = null;
          let processedResponseTimings: CourseTimings[] = result.timings.map(
            (timing) => {
              return {
                weekday: new Date(timing.start).getDay(),
                start: new Date(timing.start),
                end: new Date(timing.end),
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
          } as CourseCardProps;
          }) 
          

          console.log(JSON.stringify(courseCards));

          setSearch(courseCards);
        })
        .catch((err: Error) => {
          setRequestError(true);
          console.log("OOOO", err);
        })
        .finally(() => {

        });
    } else {
      setRequestError(true);
    }
  };

  const handleRemoveButtonClick = (crn: string) => {
    let newState = basket;
    newState = newState.filter((course) => {
      if(course.crn === crn){
        setSearch([...search, course])
      }
      return course.crn !== crn;
    });
    console.log(newState);
    setBasket(newState);
  };

  const handleAddButtonClick = (crn: string) => {
    //remove from search bar
    setSearch(search.filter((course) => {
      return course.crn !== crn;
    }))

    //add to basket
    const newClass = search.filter((course) => {
      return course.crn === crn;
    });
    setBasket([...basket, ...newClass]);
  }

  const sectionStyle: CSSProperties = {
    borderColor: "grey",
    borderWidth: "2px",
    borderStyle: "solid",
  };

  const getCalSelectStyle = (cal: UserCalendarBookItem) => {
    return {
      backgroundColor: cal.color
    } as CSSProperties
  }

  return (
    <div className="App">
      <Navigation userData={userData} />
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
          <Col xl={2} style={sectionStyle}>
            {search.map((course, index) => {
              let basketCRNs = basket.map(course => course.crn)
              if(basketCRNs.includes(course.crn)){
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
          <Col xl={2} style={sectionStyle}>
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
            <UncontrolledDropdown
              group
              size="md"
            >
              <DropdownToggle style={getCalSelectStyle(selectedCalendar)} caret> {selectedCalendar.title}</DropdownToggle>
              <DropdownMenu>
                {userData.calendar_book?.map((cal, index) => {
                  const selected = cal.id == selectedCalendar.id
                  return <DropdownItem active={selected} key={index} onClick={() => setSelectedCalendar(cal)}>{cal.title}</DropdownItem>
                })}
              </DropdownMenu>
            </UncontrolledDropdown>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
