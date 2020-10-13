import time
import datetime

date_conv = '%Y-%m-%d %H:%M:%S.%f%z'

NO_SECONDS = '%Y-%m-%d %H:%M'

STRF_DATE = '%d-%m-%Y'
STRF_TIME = '%H:%M'


def get_time_str(dt, local=True, date=True, time=True, seconds=False, microseconds=False):
    """
    Converts a datetime to a string based on the parameters.
    :param dt:
    :param local:
    :param date:
    :param time:
    :param seconds:
    :param microseconds:
    :return:
    """
    strf_str = create_strf_str(date, time, seconds, microseconds)

    if local:
        return (dt + dt.utcoffset()).strftime(strf_str)
    else:
        return dt.strftime(strf_str)


def meas_to_time(meas, seconds=False):
    """
    Converts a measurement (from db model) to a string
    :param meas:
    :param seconds:
    :return:
    """
    return get_time_str(meas.timestamp, date=False, seconds=seconds)


def create_strf_str(date=True, time=True, seconds=False, microseconds=False):
    """
    Return a format string based on the parameters.
    :param date:
    :param time:
    :param seconds:
    :param microseconds:
    :return:
    """
    strf_str = ''

    if date:
        strf_str += STRF_DATE
    if date and time:
        strf_str += ' '
    if time:
        strf_str += STRF_TIME
    if seconds:
        strf_str += ':%S'
    if microseconds and seconds:
        strf_str += '.%f'

    return strf_str


def convert_to_datetime(input):
    time_string = input[:-3] + input[-2:]
    return datetime.datetime.strptime(time_string, date_conv)



# time1 - time2
def clean_diff(time1, time2):
    """
    Return diff in time in seconds with a negative diff if time2 > time1.
    :param time1:
    :param time2:
    :return:
    """
    diff = abs_diff(time1, time2)

    if time2 > time1:
        return -1 * diff
    else:
        return diff


def abs_diff(time1, time2):
    """
    Return abs diff between two times in seconds.
    :param time1:
    :param time2:
    :return:
    """
    if time1 > time2:
        diff = time1 - time2
    else:
        diff = time2 - time1

    sec_diff = diff.days * 24 * 60 * 60 + diff.seconds + diff.microseconds * 0.000001

    return sec_diff


if __name__ == "__main__":
    s1 = '2019-02-28 15:00:39.749340+01:00'
    s2 = '2019-02-28 15:00:39.749680+01:00'

    t1 = convert_to_datetime(s1)
    t2 = convert_to_datetime(s2)

    print(t1)
    print(t1.combine(t1.date(), t1.timetz()))
    print(t1.tzinfo)
    print(t1.utcoffset())
    print(t1 + t1.utcoffset())
