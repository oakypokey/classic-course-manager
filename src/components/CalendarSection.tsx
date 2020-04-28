import React, { useEffect, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import rrulePlugin from "@fullcalendar/rrule"

import "@fullcalendar/core/main.css";
import "@fullcalendar/daygrid/main.css"
import "@fullcalendar/timegrid/main.css";
import { CourseCardProps } from "./CourseCard";
import { ExtendedEventSourceInput } from "@fullcalendar/core/structs/event-source";
import { EventSourceFunc } from "@fullcalendar/core/event-sources/func-event-source";
import { EventInput, Calendar } from "@fullcalendar/core";
import { durationsEqual } from "@fullcalendar/core/datelib/duration";

interface CalendarSectionProps {
  events: CourseCardProps[];
  academicCalEvents: EventProperties[];
}

export interface EventProperties {
  start: Date;
  end: Date;
  title: string;
  allDay: boolean;
  rrule?: string
  duration: string
  color: string
}

export const CalendarSection: React.FC<CalendarSectionProps> = ({
  events,
  academicCalEvents,
}: CalendarSectionProps) => {
    const [defaultDate, setDefaultDate] = useState(new Date())
    const calendarRef: React.RefObject<FullCalendar> = React.createRef()
    const [allEvents, setAllEvents] = useState(academicCalEvents)
   

    const getStartEndTime = (events: EventProperties[]): resultProperties => {
      let result = {
        startTime: "08:00",
        endTime: "17:45",
        defaultDate: new Date(),
      };
  
      if(events.length < 1){
          return result
      }
  
      events.sort((a, b) => {
        return a.start > b.start ? 1 : -1;
      });
  
      result.defaultDate = events[0].start
  
      let startHour = (events[0].start.getHours() - 1).toString();
      let startMin = events[0].start.getMinutes().toString();
      startHour = ("00000" + startHour).slice(-2);
      startMin = ("00000" + startMin).slice(-2);
  
      let endHour = (events[events.length - 1].end.getHours() + 1).toString();
      let endMin = events[events.length - 1].end.getMinutes().toString();
      endHour = ("00000" + endHour).slice(-2);
      endMin = ("00000" + endMin).slice(-2);
  
      const lateHours = events[events.length - 1].end.getHours() > 17;
      const earlyHours = events[0].start.getHours() < 8;
  
      if (
        !(
          events[events.length - 1].end.getHours()  - events[0].start.getHours() >=
            7 ||
          lateHours ||
          earlyHours
        )
      ) {
        result.startTime = `${startHour}:${startMin}`;
        result.endTime = `${endHour}:${endMin}`;
      }
  
      return result;
    };

  const [maxMinTime, setMaxMinTime]  = useState(getStartEndTime(allEvents))

  useEffect(() => {
      //TODO: accomodate for course events as well
      const allEvents = [...academicCalEvents]
      const calendarObj = calendarRef.current
      if(calendarObj){
        const calendarAPI = calendarObj.getApi()

        const sortedEvents = allEvents.sort((a, b) => {
            return a.start > b.start ? 1 : -1;
          });
        
        if(allEvents.length > 1){
            calendarAPI.gotoDate(sortedEvents[0].start)
        }
        
      }

      setAllEvents(academicCalEvents)
  }, [academicCalEvents])

  interface resultProperties {
    startTime: string;
    endTime: string;
    defaultDate: Date;
  }

  useEffect(() => {
    let newEventState: EventProperties[] = []

    const timeFix = events.map((event) => {
      let newEvent = event
      let newTimings = event.timings?.map((e) => {
        return {
          start: new Date(e.start),
          end: new Date(e.end),
          weekday: e.weekday,
          rrule: e.rrule,
          duration: e.duration
        }
      })
      
      newEvent.timings = newTimings
      return newEvent
    })

    timeFix.forEach((course) => {
      course.timings?.forEach((session) => {
        newEventState.push({
          start: session.start,
          end: session.end,
          title: course.courseName,
          allDay: false,
          rrule: session.rrule,
          duration: session.duration,
          color: course.color
        })
      })
    })
    
    console.log("this is new event state", newEventState)
    setAllEvents([...academicCalEvents, ...newEventState])
    setMaxMinTime(getStartEndTime([...newEventState]))
  }, [events])

  

  return (
    <>
      {maxMinTime.startTime}
      {maxMinTime.endTime}
      <FullCalendar
        events={allEvents}
        defaultView="timeGridWeek"
        plugins={[timeGridPlugin, interactionPlugin, rrulePlugin]}
        weekends={false}
        slotDuration={{ minutes: 30 }}
        minTime={"07:30"}
        maxTime={"22:45"}
        slotEventOverlap={true}
        allDaySlot={true}
        slotLabelInterval={{ minutes: 90 }}
        ref={calendarRef}
      ></FullCalendar>
    </>
  );
};
