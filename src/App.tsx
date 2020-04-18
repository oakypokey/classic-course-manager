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

import { CourseSearch } from "./components/CourseSearch";

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
} from "reactstrap";
import { CalendarSection, EventProperties } from "./components/CalendarSection";
import { Session } from "inspector";

interface APIResponse {
  error: boolean;
  results: APIResponseCourse[];
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
}

interface APIResponseTimingsData {
  allDay: boolean;
  end: string;
  start: string;
  title: string;
  crn: number;
  id: number;
}

interface AcademicCalEventProperties{
  start: AcademicCalDateProperties
  end: AcademicCalDateProperties
  summary: string
  description: string
}

interface AcademicCalDateProperties{
  date?: string
  dateTime?: string
  timeZone?: string
}

interface AcademicCalEventsResponseProperties{
  last_fetched: string
  events: AcademicCalEventProperties[]
  error: boolean
  message?: string
}

export interface SessionUserData {
  email: string
  email_verified: boolean
  family_name: string
  given_name: string
  locale: string
  name: string
  nickname: string
  picture: string
  sub: string
  updated_at: string
}

function App() {
  const [inputCRN, setInputCRN] = useState("");
  const [basket, setBasket] = useState([] as CourseCardProps[]);
  const [requestError, setRequestError] = useState(false);
  const [academicCalEvents, setAcademicCalEvents] = useState([] as EventProperties[])
  const [userData, setUserData] = useState({} as SessionUserData)

  //Just like component did mount <3
  useEffect(() => {
    fetch('/api/getacademiccalinfo').then(res => res.json()).then((response: AcademicCalEventsResponseProperties) => {
      let AcademicCalEventsProcessed = [] as EventProperties[]
      if(response.error){
        console.log("Error when fetching response: " + response.message)
        return
      }

      AcademicCalEventsProcessed = response.events.map((event) => {
        let startTime = new Date()
        let endTime = new Date()

        if(event.start.date && event.end.date){
          startTime = new Date(Date.parse(event.start.date))
          startTime = new Date(Date.parse(event.end.date))
        } else if(event.start.dateTime && event.end.dateTime) {
          startTime = new Date(Date.parse(event.start.dateTime))
          endTime = new Date(Date.parse(event.end.dateTime))
        }
      
        const allDayBool = (startTime.getTime() - endTime.getTime()) > (1000 * 60 * 60 * 23)
        console.log((startTime.getTime() - endTime.getTime()) > (1000 * 60 * 60 * 23))
        return {
          start: startTime,
          end: endTime,
          title: event.summary,
          allDay: allDayBool
        } as EventProperties
      })
      console.log(AcademicCalEventsProcessed)
      setAcademicCalEvents(AcademicCalEventsProcessed)

      fetch('/api/user_data').then(res => res.json()).then(data => {setUserData(data.session as SessionUserData)})
    })
  }, [])

  const handleCRNSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setRequestError(false);
    if (
      basket.filter((course) => {
        return course.crn == inputCRN;
      }).length < 1
    ) {
      fetch("/api/getinfo?crn=" + inputCRN)
        .then((res: Response) => {
          let result: Promise<APIResponse> = res.json();
          return result;
        })
        .then((result) => {
          if (result.error) {
            throw new Error("Course does not exist.");
          }
          return result;
        })
        .then((response) => {
          let processedResponse: CourseCardProps | null = null;
          let processedResponseTimings: CourseTimings[] = response.results[0].timings.map(
            (timing) => {
              return {
                weekday: new Date(timing.start).getDay(),
                start: new Date(timing.start),
                end: new Date(timing.end),
              };
            }
          );

          processedResponse = {
            courseName: response.results[0].name,
            subjectName: response.results[0].sname,
            section: response.results[0].section,
            professorName: response.results[0].professor__name,
            crn: response.results[0].crn.toString(),
            timings: processedResponseTimings,
          } as CourseCardProps;

          console.log(JSON.stringify(processedResponse));

          setBasket([...basket, processedResponse]);
        })
        .catch((err: Error) => {
          setRequestError(true);
          console.log("OOOO", err);
        })
        .finally(() => {
          setInputCRN("");
        });
    } else {
      setInputCRN("");
      setRequestError(true);
    }
  };

  const handleRemoveButtonClick = (crn: string) => {
    let newState = basket;
    newState = newState.filter((course) => {
      return course.crn !== crn;
    });
    console.log(newState);
    setBasket(newState);
  };

  const sectionStyle: CSSProperties = {
    borderColor: "grey",
    borderWidth: "2px",
    borderStyle: "solid"
  }

  return (
    <div className="App">
      <Navigation userData={userData}/>
      <Container fluid>
        <Row>
          <Col xl={6}>
          <CourseSearch
              handleCRNSubmit={handleCRNSubmit}
              setInputCRN={setInputCRN}
              inputCRN={inputCRN}
              requestError={requestError}
            />
            {requestError ? <UncontrolledAlert label={"errmsg"} color={"danger"}>
              There was an error. Please try again.
            </UncontrolledAlert> : ''}
          </Col>
          <Col xl={6}>
            <Container>
              <Row>
              <Col xs={4}>Something</Col><Col xs={4}>Something</Col><Col xs={4}>Something</Col>
              </Row>
              <Row>
              <Col xs={4}>Something</Col><Col xs={4}>Something</Col><Col xs={4}>Something</Col>
              </Row>
            </Container>
          </Col>
        </Row>
        <Row>
        <Col xl={3} style={sectionStyle}>
            
            {basket.map((course, index) => {
              return (
                <CourseCard
                  key={index}
                  handleRemoveButtonClick={handleRemoveButtonClick}
                  {...course}
                />
              );
            })}
          </Col>
          <Col xl={3} style={sectionStyle}>
            {basket.map((course, index) => {
              return (
                <CourseCard
                  key={index}
                  handleRemoveButtonClick={handleRemoveButtonClick}
                  {...course}
                />
              );
            })}
          </Col>
          <Col xl={6} style={sectionStyle}>
            <CalendarSection events={basket} academicCalEvents={academicCalEvents}/>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
