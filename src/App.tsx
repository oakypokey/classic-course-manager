import React, { useState } from "react";
import logo from "./logo.svg";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { Navigation } from "./components/Navigation";
import { CourseCard, CourseCardProps, CourseTimings } from "./components/CourseCard";

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
} from "reactstrap";

interface APIResponse{
  error: boolean
  results: APIResponseCourse[]
}

interface APIResponseCourse{
  crn: number
  level: string
  multiple_sections: boolean
  name: string
  professor__name: string
  remaining: number
  section: string
  show_xlist: boolean
  sname: string
  waitlistact: number
  timings?: CourseTimings[]
}

interface APIResponseTimings{
  error: boolean
  data: APIResponseTimingsData[]
}

interface APIResponseTimingsData{
  allDay: boolean
  end: string
  start: string
  title: string
  crn: number
  id: number
}

function App() {
  const [inputCRN, setInputCRN] = useState("");
  const [basket, setBasket] = useState([] as CourseCardProps[]);
  const [requestError, setRequestError] = useState(false)

  const handleCRNSubmit = () => {
    setRequestError(false)
    fetch("/api/getinfo?crn=" + inputCRN)
      .then((res: Response) => {
        let result: Promise<APIResponse> = res.json()
        console.log("getInfo", result)
        return result
      }).then((result) => {
        let data = result
        if(result.error){
          throw new Error("Course does not exist.")
        }

        fetch("/api/getcoursetimings?crn=" + result.results[0].crn.toString()).then((res: Response) => {
          let result: Promise<APIResponseTimings> = res.json()
          console.log("getCourseTimings", result)
          return result
        }).then((res) => {
          let payload = res.data.map((timing: APIResponseTimingsData) => {
            return {
              weekday: new Date(timing.start).getDay(),
              start: new Date(timing.start),
              end: new Date(timing.end)
            } as CourseTimings
          })
          data.results[0].timings = payload
        }).catch(e => {
          setRequestError(true)
          throw new Error("getCourseTimings")
        })

        return data
      })
      .then((response) => {
        let processedResponse: CourseCardProps | null = null
        
        processedResponse = {
          courseName: response.results[0].name,
          subjectName: response.results[0].sname,
          section: response.results[0].section,
          professorName: response.results[0].professor__name,
          timings: response.results[0].timings
        } as CourseCardProps

        console.log(JSON.stringify(processedResponse));
        
        setBasket([...basket, processedResponse])
      })
      .catch((err: Error) => {
        console.log("OOOO", err);
        
      })
      .finally(() => {
        setInputCRN("");
      });
  };

  return (
    <div className="App">
      <Navigation />
      {requestError ? "true" : "false"}
      <Container>
        <Row>
          <Col lg={3}>
            <form onSubmit={handleCRNSubmit}>
              <InputGroup>
                <InputGroupAddon addonType="prepend">
                  <InputGroupText>CRN</InputGroupText>
                </InputGroupAddon>
                <Input
                  name={"crn"}
                  value={inputCRN}
                  onChange={(e) => setInputCRN(e.target.value)}
                  placeholder="12345"
                  invalid={requestError}
                />
              </InputGroup>
            </form>
            {basket.map((course, index) => {
              return <CourseCard key={index} {...course} />;
            })}
          </Col>
          <Col lg={9}></Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;

const DUMMYDATA: CourseCardProps[] = [
  {
    courseName: "Digital Design I",
    subjectName: "ARTS 100",
    section: "02",
    professorName: "Mike Wang",
    timings: [
      {
        weekday: 1,
        start: new Date(),
        end: new Date(),
      },
      {
        weekday: 3,
        start: new Date(),
        end: new Date(),
      },
    ],
    conflict: true,
  },
];
