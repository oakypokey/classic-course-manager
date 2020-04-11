import React from "react";
import FullCalendar from "@fullcalendar/react";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";

import "@fullcalendar/core/main.css";
import "@fullcalendar/timegrid/main.css";
import { CourseCardProps } from "./CourseCard";
import { ExtendedEventSourceInput } from "@fullcalendar/core/structs/event-source";
import { EventSourceFunc } from "@fullcalendar/core/event-sources/func-event-source";
import { EventInput } from "@fullcalendar/core";
import { durationsEqual } from "@fullcalendar/core/datelib/duration";

interface CalendarSectionProps {
  events: CourseCardProps[];
}

interface EventProperties {
  start: Date;
  end: Date;
  title: string;
  allDay: boolean;
}

export const CalendarSection: React.FC<CalendarSectionProps> = ({
  events,
}: CalendarSectionProps) => {
  const startDate = new Date("2020/04/09 08:00");
  const endDate = new Date("2020/04/09 09:00");

  const dummyEvents = [
    {
      start: startDate,
      end: endDate,
      title: "Example Event",
      allDay: false,
    },
    {
        start: new Date("2020/04/09 12:00"),
        end: new Date("2020/04/09 15:00"),
        title: "Example Event2",
        allDay: false,
      },
  ];

  const allEvents = dummyEvents

  const getStartEndTime = (events: EventProperties[]) => {
      if(events.length < 1){
          return undefined
      }

    let result = {
        startTime: "",
        endTime: ""
    }

    events.sort((a, b) => {
      return a.start > b.start ? 1 : -1;
    });

    let startHour = (events[0].start.getHours() - 1).toString()
    let startMin = (events[0].start.getMinutes()).toString()
    startHour = ('00000'+startHour).slice(-2)
    startMin = ('00000'+startMin).slice(-2)

    let endHour = (events[events.length - 1].end.getHours() + 1).toString()
    let endMin = (events[events.length - 1].end.getMinutes()).toString()
    endHour = ('00000'+ endHour).slice(-2)
    endMin = ('00000'+ endMin).slice(-2)

    result.startTime = `${startHour}:${startMin}`
    result.endTime = `${endHour}:${endMin}`

    console.log(result)
    const lateHours = events[events.length-1].end.getHours() > 17
    const earlyHours = events[0].start.getHours() < 8

    if((events[0].start.getHours() - events[events.length -1].end.getHours()) >= 4 || lateHours || earlyHours){
        return result
    } else {
        return undefined
    }
  };

  // TODO: format calendar objects properly and have them output onto the screen calendar
  return (
    <>
      <FullCalendar
        events={allEvents}
        defaultView="timeGridWeek"
        plugins={[timeGridPlugin, interactionPlugin]}
        weekends={false}
        slotDuration={{ minutes: 30 }}
        minTime={getStartEndTime(allEvents)?.startTime || "08:00"}
        maxTime={getStartEndTime(allEvents)?.endTime || "17:45"}
        slotEventOverlap={true}
        allDaySlot={true}
        slotLabelInterval={{ minutes: 90 }}
      ></FullCalendar>
    </>
  );
};
