import tkinter as tk
from tkinter import filedialog, Text
import os
import datetime
from google_calendar import getGoogleCalendarAPI


root = tk.Tk()
root.title("Class 2 Calendar")

canvas = tk.Canvas(root, height=700, width=700, bg="#263D42")

frame = tk.Frame(root, bg="white")

service = getGoogleCalendarAPI()

now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
print('Getting the upcoming 10 events')
# pylint: disable=no-member
events_result = service.events().list(calendarId='primary', timeMin=now,
                                    maxResults=10, singleEvents=True,
                                    orderBy='startTime').execute()
events = events_result.get('items', [])

if not events:
    print('No upcoming events found.')
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(start, event['summary'])
    lbl = tk.Label(root, text=event['summary'])
    lbl.pack()

canvas.pack()
root.mainloop()