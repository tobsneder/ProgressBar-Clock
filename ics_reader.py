from datetime import datetime, timedelta, timezone
import icalendar
import pytz


class ics_reader:
    def __init__(self, file):
        self.local_tz = pytz.timezone('Europe/Vienna')
        self.ico_file = file
        self.lessons = []

    def utc_to_local(self, utc_dt):
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(self.local_tz)
        return self.local_tz.normalize(local_dt)

    def parse(self):
        self.lessons.clear()
        icalfile = open(self.ico_file, 'rb')
        gcal = icalendar.Calendar.from_ical(icalfile.read())

        for component in gcal.walk():
            if component.name == "VEVENT":
                summary = component.decoded('summary').decode("utf-8")
                startdt = self.utc_to_local(component.get('dtstart').dt)
                enddt = self.utc_to_local(component.get('dtend').dt)

                self.lessons.append([summary, startdt, enddt])
        icalfile.close()

    def get_current_lesson(self):
        self.parse()
        currentdt = datetime.now().astimezone(self.local_tz)
        for lesson in self.lessons:
            if lesson[1] < currentdt < lesson[2]:
                return [lesson[0].split(" ", 2)[1], lesson[1], lesson[2]]  # title, startdt, enddt

    def get_current_day(self):
        self.parse()
        currentdt = datetime.now().astimezone(self.local_tz)
        lesson_starts = []
        lesson_ends = []
        for lesson in self.lessons:
            if lesson[1].day == currentdt.day and lesson[2].day == currentdt.day:
                lesson_starts.append(lesson[1])
                lesson_ends.append(lesson[2])

        startdt = lesson_starts[0]  # just assign any date to compare to
        enddt = lesson_ends[0]
        for start in lesson_starts:
            if start < startdt:
                startdt = start

        for end in lesson_ends:
            if end > enddt:
                enddt = end

        if startdt < currentdt < enddt:
            return ["day", startdt, enddt]

    def get_current_week(self):
        self.parse()
        currentdt = datetime.now().astimezone(self.local_tz)
        lesson_starts = []
        lesson_ends = []
        for lesson in self.lessons:
            lesson_starts.append(lesson[1])
            lesson_ends.append(lesson[2])

        startdt = lesson_starts[0]  # just assign any date to compare to
        enddt = lesson_ends[0]
        for start in lesson_starts:
            if start < startdt:
                startdt = start

        for end in lesson_ends:
            if end > enddt:
                enddt = end

        if startdt < currentdt < enddt:
            return ["week", startdt, enddt]








