# coding:utf-8

import math
from app_core import app
import base64, hashlib, random, secrets


def is_number(s):
    """
    check input value is a number or not
    :param s: input value, we want to check
    :return: true if, input is a number, else false
    """
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except(TypeError, ValueError):
        pass
    return False


# ---------------------------------------------------------------------------------------------------------------------+

def dms2decimal(in_degree=0, in_minute=0, in_second=0, in_direction='n'):
    """
    convert Degree Minutes Second(DMS) coordinate to  decimal
    :param in_degree: number format degree
    :param in_minute:  input minute
    :param in_second: input second
    :param in_direction: Direction mus be north, south, east and west in lower case
    :return: decimal number
    """

    d = in_direction.lower()
    direction = ['n', 's', 'e', 'w']

    # Degree must be integer range in 0 and 180
    if not is_number(in_degree) or in_degree < 0 or in_degree > 180:
        decimal = False
    # Minute must be integer or float  range from 0 to 59
    elif not is_number(in_minute) or in_minute < 0 or in_minute > 59:
        decimal = False

    # Second must be integer or float range from 0 and 59
    elif not is_number(in_second) or in_second < 0 or in_second > 59:
        decimal = False
    elif in_direction not in direction:
        decimal = False
    else:
        # input are validated
        decimal = in_degree + (in_minute * 0.01666667) + (
            in_second * 0.000277778)  # igual inMinute / 60 and inSecond/3600, in python 3

        if d == 's' or d == 'w':  # if the direction is South or West,, return negative value.
            decimal *= -1
    return "%.6f" % decimal


@app.context_processor
def my_utility_processor():
    def decimal_second_to_hms(input_decimal):
        """
        Convert decimal second into HH:mm:ss
        :param input_decimal: insert number we want to convert
        :return: time format: ex- 12:02:05
        """
        if not is_number(input_decimal):
            time = False
        else:
            hour, rest = divmod(input_decimal, 3600)
            minute, second = divmod(rest, 60)
            time = "%02d:%02d" % (hour, minute)  # we just used Hour and Minutes
        return time

    return dict(convertdecimaltotime=decimal_second_to_hms)  # end my_utility processor


@app.context_processor
def my_utility_processor1():
    def decimal2dms(in_decimal):
        """
        Convert decimal to Degree, minutes and second(DMS)
        :param in_decimal: input number we want to convert it
        :return: degree, minutes and second(DMS)
        """
        direction = True
        # decimal must be integer or float and less than 180
        if not is_number(in_decimal or abs(in_decimal) > 180):
            return False

        # Input valid proceed
        if in_decimal < 0:
            direction = False
        # get the abs value of decimal
        d = abs(float(in_decimal))
        degree = int(math.floor(d))  # get degrees
        second = (d - degree) * 3600  # get seconds
        minutes = int(math.floor(second / 60))
        second = int(math.floor(second - (minutes * 60)))
        dms = {"degree": degree, "minute": minutes, "second": second, "direction_state": direction}
        return dms

    return dict(convert_decimalto_dms=decimal2dms)  # end my_utility processor1


# ---------------------------------------------------------------------------------------------------------------------+


@app.context_processor
def my_utility_processor2():
    def format_datetime(dt):
        return dt.strftime("%Y-%m-%d  %H:%M")

    return dict(date_time=format_datetime)

# convert time 02:30 to format 02 h 30 m
@app.context_processor
def my_utility_processor3():
    def decimal_second_to_hms(input_decimal):
        """
        Convert decimal second into HH:mm:ss
        :param input_decimal: insert number we want to convert
        :return: time format: ex- 12:02:05
        """
        if not is_number(input_decimal):
            time = False
        else:
            hour, rest = divmod(input_decimal, 3600)
            minute, second = divmod(rest, 60)
            time = "%02d h %02d m" % (hour, minute)  # we just used Hour and Minutes
        return time

    return dict(convertdecimaltotime1=decimal_second_to_hms)  # end my_utility processor


# Convert time in to  decimal(second)
def convert_time_to_decimal(input_time_str):
    h, m = input_time_str.split(':')
    return int(h) * 3600 + int(m) * 60


def convert_time_to_decimalv2(*input_time_str):
    for item in input_time_str:
        h, m = item.split(':')
        return int(h) * 3600 + int(m) * 60


# convert duration format ("5 hours 30 minutes) to format ("5:30")
def convert_duration_to_standard_time(input_time):
    my_list = [item.split() for item in input_time]
    result = []
    for i in range(len(my_list)):
        if len(my_list[i]) == 2:
            aux = my_list[i][0]  #
            if my_list[i][1] == "m":
                minutes = aux
                if minutes < 10:
                    minutes = "0%d" % minutes
                hours = "00"
            else:
                hours = aux
                if hours < 10:
                    hours = "0%d" % hours
                minutes = "00"

            t1 = "%s:%s" % (hours, minutes)
            result.append(t1)
        elif len(my_list[i]) == 4:
            hours = my_list[i][0]
            if hours < 10:
                hours = "0%d" % hours
            minutes = my_list[i][2]

            t2 = "%s:%s" % (hours, minutes)
            result.append(t2)
    return result


def convert_duration_to_decimal_tes(*input_time):
    print(len(input_time))

def generate_hash_key():
    return hashlib.sha256(str(secrets.randbits(256)).encode('utf-8')).hexdigest()