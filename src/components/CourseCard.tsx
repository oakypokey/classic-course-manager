import React, { useState } from "react";
import {
  Card,
  CardText,
  CardBody,
  CardTitle,
  CardSubtitle,
  Button,
  Badge,
} from "reactstrap";

export interface CourseTimings {
  weekday: number
  start: Date
  end: Date
}

export interface CourseCardProps {
  courseName: string;
  subjectName: string;
  section: string;
  professorName: string;
  timings?: CourseTimings[];
  conflict?: boolean;
  crn: string;
  handleRemoveButtonClick?: any
  handleAddButtonClick?: any
  basket: boolean
}

const CourseCardStyle: React.CSSProperties = {
  padding: "10px",
  margin: "5px",
  textAlign: "left"
};

const TimingStyle: React.CSSProperties = {
  fontSize: "0.85vw"
};

const ConflictStyle: React.CSSProperties = {
  width: "40%"
};

export const CourseCard: React.FC<CourseCardProps> = ({
  courseName,
  subjectName,
  section,
  professorName,
  timings,
  conflict,
  handleRemoveButtonClick,
  handleAddButtonClick,
  crn,
  basket
}: CourseCardProps) => {

  const getTimeString = (date: Date) => {
    let hours = date.getHours();
    let minutes: string | number = date.getMinutes();
    let ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
  }

  return (
    <>
      <Card style={CourseCardStyle}>
        <CardTitle>
          <h4>{courseName}</h4>
          {conflict ? (
            <Badge style={ConflictStyle} pill color="danger">
              CONFLICT
            </Badge>
          ) : (
            ""
          )}
        </CardTitle>
        <CardSubtitle>
            {subjectName} - {section}
          </CardSubtitle>
          <CardSubtitle>Professor {professorName}</CardSubtitle>
          <br/>
          {timings?.map((time, index) => {
            return (
              <CardSubtitle key={index} style={TimingStyle}>
                {time.weekday}: {getTimeString(time.start)} to {getTimeString(time.end)}
              </CardSubtitle>
            );
          })}
          {
            basket ? <Button color="danger" onClick={() => {handleRemoveButtonClick(crn)}}> Remove from Basket </Button> : <Button color="primary" onClick={() => {handleAddButtonClick(crn)}}> Add to Basket </Button>
          }
        
      </Card>
    </>
  );
};

