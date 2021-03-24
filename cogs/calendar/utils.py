from datetime import datetime, timedelta
from icalendar import Calendar

import copy
import discord
import time
import os
import requests

CALENDAR_PATH = "cogs/calendar/Assets/3TCA.ical"
WEEKDAYS = {1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi"}
RESPONSE_TEMPLATE = """{starting_time}:00 - {end_time}:00 :: {course} at {location} | {details}"""
COURSE_COMMENT = {}
DETAILS_COMMENT = {"Image": "ui"}


def get_course_starting_time():
    """
    This function gets the starting time of a course.
    """
    now = datetime.now()
    if 8 < now.hour < 10:
        return datetime(now.year, now.month, now.day, 8, 0, 2)
    if 10 < now.hour < 12:
        return datetime(now.year, now.month, now.day, 10, 0, 2)
    if 14 < now.hour < 16:
        return datetime(now.year, now.month, now.day, 16, 0, 2)
    return datetime(now.year, now.month, now.day, 18, 0, 2)


def get_current_course(calendar_path):
    """
    Get the current course
    """
    with open(calendar_path, "rb") as file:
        calendar = Calendar.from_ical(file.read())
    for component in calendar.walk():
        if component.name == "VEVENT" and component['DTSTART'].dt == datetime.now():
            return component


def get_course_by_date(prompt_date=datetime.now().date(), calendar_path=CALENDAR_PATH):
    """
    Get courses by their date.
    """
    courses = []
    with open(calendar_path, 'rb') as file:
        calendar = Calendar.from_ical(file.read())
    for component in calendar.walk():
        if component.name == "VEVENT" and component['DTSTART'].dt.date() == prompt_date:
            courses.append(component)
            if len(component) == 4:
                break

    return courses


def format_response(course, template=RESPONSE_TEMPLATE):
    """
    Format the response to send to the server
    """
    try:
        starting_time = format_time(course, 'DTSTART')
        end_time = format_time(course, 'DTEND')
        current_course = format_course(course)
        location = format_location(course)
        details = format_details(course)
        return template.format(
            starting_time=starting_time,
            end_time=end_time,
            course=current_course,
            location=location,
            details=details
        )
    except:
        return "The programmer is bad"


def format_course(course):
    """
    Format the course infos displayed
    """
    current_course = course['SUMMARY']
    name = current_course[current_course.index('-') + 1:current_course.index('/')]
    i = len(current_course) - 1

    while i != 0:
        if current_course[i] == '/':
            break
        i -= 1
    begin_strip = current_course.index('_') if '_' in current_course else current_course.index('/')
    course_type = current_course[begin_strip + 1:i]
    comment = ""
    if name in COURSE_COMMENT.keys():
        comment = f" {COURSE_COMMENT[name]}"

    return f"{name} {course_type}{comment}"


def format_time(course, course_time):
    """
    Format the course time displayed
    """
    return str(course[course_time].dt.hour).zfill(2)


def format_location(course):
    """
    Format the course location displayed
    """
    if "Distanciel" in course['LOCATION']:
        return "Distanciel"
    return course['LOCATION']


def format_details(course):
    """
    Format the course details displayed
    """
    comment = ""
    description = course['DESCRIPTION']
    for key in description:
        if key in DETAILS_COMMENT.keys():
            comment = f" {DETAILS_COMMENT[key]}"
            break
    return f"{description}{comment}"


def download_calendar():
    """
    Download the TC calendars for each group
    """
    url_template = "http://tc-net2.insa-lyon.fr/aff/AffichageEdtPalmGroupe.jsp" \
                   "?promo={year}&groupe={group}&dateDeb=1604856847608"
    assets_dir = "cogs/calendar/Assets"
    years = ["3", "4", "3A", "4A", "5"]
    groups = range(1, 4)

    for year in years:
        for group in groups:
            if "A" in year and group in [2, 3]:
                continue
            download_url = url_template.format(year=year, group=group)
            formatted_group_name = group if "A" not in year else "A"
            formatted_year_name = year if "A" not in year else year[0]
            filename = f"{formatted_year_name}TC{formatted_group_name}.ical"
            path = os.path.join(assets_dir, filename)

            result = requests.get(download_url)
            with open(path, "wb") as file:
                file.write(result.content)

            time.sleep(1)


def get_week_calendar(calendar_path=CALENDAR_PATH, offset=0, dobby=None, group_displayed="3TCA"):
    """
    Get the calendar of a week
    """
    current_weekday = datetime.today().isoweekday()
    week_calendar = {}
    calendar = discord.Embed()
    calendar.description= "Calendrier des " + group_displayed
    weekdays_with_date = {}

    for day_index in range(0, current_weekday):
        day = datetime.today() - timedelta(days=day_index) + timedelta(days=offset * 7)

        if day_index + 1 in WEEKDAYS:
            weekdays_with_date[day_index + 1] = WEEKDAYS[day_index + 1] + " " + str(day.day) + "/" + str(day.month)
        if day_index == 0:
            calendar.title = "Semaine du " + str(day.day) + "/" + str(day.month)

        week_calendar[current_weekday - day_index] = get_course_by_date(
            prompt_date=day.date(),
            calendar_path=calendar_path
        )

    for day_index in range(current_weekday, 6):
        day = datetime.today() + timedelta(days=day_index + 1 - current_weekday) + timedelta(days=offset * 7)
        if day_index + 1 in WEEKDAYS:
            weekdays_with_date[day_index + 1] = WEEKDAYS[day_index + 1] + " " + str(day.day) + '/' + str(day.month)
        if day_index == 0:
            calendar.title = "Semaine du " + str(day.day) + "/" + str(day.month)

        week_calendar[day_index + 1] = get_course_by_date(
            prompt_date=day.date(),
            calendar_path=calendar_path
        )

    for day_index in range(1, 7):
        formatted_courses = []
        is_4_hour_course = False
        for course_beginning_time in [8, 10, 14, 16]:
            if is_4_hour_course:
                is_4_hour_course = False
                continue
            is_changed = False
            for course in week_calendar[day_index]:
                if course['DTSTART'].dt.hour == course_beginning_time:
                    if course['DTEND'].dt.hour - course['DTSTART'].dt.hour == 4:
                        formatted_courses += [format_course(course)] * 2
                        is_4_hour_course = True
                    else:
                        formatted_courses.append(format_course(course))
                    is_changed = True
                    break
            if not is_changed:
                formatted_courses.append(str(dobby))
        week_calendar[day_index] = formatted_courses
    for day_index in range(1, 6):
        calendar.add_field(
            name=weekdays_with_date[day_index],
            value=str('\n'.join(map(str, week_calendar[day_index]))),
            inline=True
        )

    return calendar


def get_offset(input_offset):
    """
    Get the offset depending on the current day
    """
    offset = 0
    if input_offset[0] == "+":
        offset = int(input_offset[1:])
    elif input_offset[0] == "-":
        offset = - int(input_offset[1:])
    if input_offset == "+0" and datetime.today().isoweekday() in [6, 7]:
        offset = 1

    return offset
