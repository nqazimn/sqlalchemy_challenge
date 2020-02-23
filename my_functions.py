# import
def get_date_str(date_object):
    """
    Summary: Returns date string (YYYY-MM-DD) for comparison in given Hawaii sqlite database

    Input: date_object as datetime object
    Output: formatted date_object_str in string format for comparison in queries
    """
    month_int = date_object.month
    year_int = date_object.year
    day_int = date_object.day

    if (month_int < 10):
        month_str = '0' + str(month_int)
    else:
        month_str = str(month_int)

    if (day_int < 10):
        day_str = '0' + str(day_int)
    else:
        day_str = str(day_int)

    date_object_str = str(year_int) + '-' + month_str + '-' + day_str

    return date_object_str
