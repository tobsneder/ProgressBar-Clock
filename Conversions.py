import time
import datetime
import pytz


def utc_to_local(utc_dt):
    local_tz = pytz.timezone('Europe/Vienna')
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def unix_to_string(unix_time):
    return utc_to_local(datetime.datetime.utcfromtimestamp(unix_time)).strftime('%Y-%m-%d %H:%M:%S')


def datetime_to_unix(dt):
    return int(time.mktime(dt.timetuple()))


def unix_to_datetime(unix_time):
    return utc_to_local(datetime.datetime.utcfromtimestamp(unix_time))
