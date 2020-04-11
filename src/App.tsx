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
import { CalendarSection } from "./components/CalendarSection";

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

function App() {
  const [inputCRN, setInputCRN] = useState("");
  const [basket, setBasket] = useState([] as CourseCardProps[]);
  const [requestError, setRequestError] = useState(false);

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
      <Navigation />
      <Container fluid>
        <Row>
          <Col xl={6}>
          <CourseSearch
              handleCRNSubmit={handleCRNSubmit}
              setInputCRN={setInputCRN}
              inputCRN={inputCRN}
              requestError={requestError}
            />
            {requestError ? <UncontrolledAlert color={"danger"}>
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
            <CalendarSection events={basket}/>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
