from Conversions import *
from configparser import ConfigParser
import webuntis
import pytz
import datetime
import time


class UntisReader:
    def __init__(self, username, password):
        self.local_tz = pytz.timezone("Europe/Vienna")

        self.config = ConfigParser()
        self.config.read("config.ini")

        self.debug_enable = False
        self.lessons = []
        self.username = username
        self.password = password

        self.session = webuntis.Session(
            username=self.username,
            password=self.password,
            server=self.config.get("Untis-API", "server"),
            school=self.config.get("Untis-API", "school"),
            useragent=self.config.get("Untis-API", "useragent")
        ).login()

    def logout(self):
        self.session.logout()

    def get_lessons(self):
        return self.lessons

    def parse(self, is_student=False, is_teacher=False, forename=None, surname=None):
        if forename is not None and surname is not None:
            self.lessons.clear()

            today = datetime.date.today()
            monday = today - datetime.timedelta(days=today.weekday())
            friday = monday + datetime.timedelta(days=4)

            if is_student:
                student = self.session.get_student(surname, forename)
                timetable = self.session.timetable(student=student, start=monday, end=friday)
            elif is_teacher:
                teacher = self.session.get_teacher(surname, forename)
                timetable = self.session.timetable(teacher=teacher, start=monday, end=friday)
            else:
                return

            for lesson in timetable:
                self.lessons.append([lesson.subjects[0].name, datetime_to_unix(lesson.start), datetime_to_unix(lesson.end)])

                if self.debug_enable:
                    print([lesson.subjects[0].name, datetime_to_unix(lesson.start), datetime_to_unix(lesson.end)])

            self.combine_double()
        else:
            raise Exception("Name not complete")

    def combine_double(self):
        new_lessons = []
        for i in self.lessons:
            new_lesson = i
            already_combined = False
            for j in self.lessons:
                if i[0] == j[0] and i != j and (i[1] == j[2] or i[2] == j[1]):
                    if j[1] < i[2]:
                        new_lesson = [i[0], j[1], i[2]]
                        if new_lesson in new_lessons:
                            already_combined = True
                        else:
                            if self.debug_enable:
                                print("combining:", i, "and", j)
                                print(new_lesson)
                                print(unix_to_string(new_lesson[1]), "to", unix_to_string(new_lesson[2]), "\n")
                    else:
                        new_lesson = [i[0], i[1], j[2]]
                        if new_lesson in new_lessons:
                            already_combined = True
                        else:
                            if self.debug_enable:
                                print("combining:", i, "and", j)
                                print(new_lesson)
                                print(unix_to_string(new_lesson[1]), "to", unix_to_string(new_lesson[2]), "\n")
            if not already_combined:
                new_lessons.append(new_lesson)

        self.lessons = new_lessons

    def get_current_lesson(self):
        current_unix = time.time()
        for lesson in self.lessons:
            if lesson[1] < current_unix < lesson[2]:
                return lesson  # title, start_unix, end_unix
        return None

    def get_current_day(self):
        current_unix = time.time()
        lesson_starts = []
        lesson_ends = []
        for lesson in self.lessons:
            if unix_to_datetime(lesson[1]).day == unix_to_datetime(current_unix).day and unix_to_datetime(lesson[2]).day == unix_to_datetime(current_unix).day:
                lesson_starts.append(lesson[1])
                lesson_ends.append(lesson[2])

        start_unix = lesson_starts[0]  # just assign any date to compare to
        end_unix = lesson_ends[0]
        for start in lesson_starts:
            if start < start_unix:
                start_unix = start

        for end in lesson_ends:
            if end > end_unix:
                end_unix = end

        if start_unix < current_unix < end_unix:
            return ["Day", start_unix, end_unix]
        return None

    def get_current_week(self):
        current_unix = time.time()
        lesson_starts = []
        lesson_ends = []
        for lesson in self.lessons:
            lesson_starts.append(lesson[1])
            lesson_ends.append(lesson[2])

        start_unix = lesson_starts[0]  # just assign any date to compare to
        end_unix = lesson_ends[0]
        for start in lesson_starts:
            if start < start_unix:
                start_unix = start

        for end in lesson_ends:
            if end > end_unix:
                end_unix = end

        if start_unix < current_unix < end_unix:
            return ["Week", start_unix, end_unix]
        return None
