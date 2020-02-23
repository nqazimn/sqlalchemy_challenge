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


def declutter_plot(plot_handle):
    '''
    Fuction to improve visualization for a plot. Removes top and right spines
    and sets color to soft gray tones to let data take center stage.

    Input: plot_handle - handle to a plot
    Output: N/A
    '''
    plot_handle.spines['right'].set_visible(False)
    plot_handle.spines['top'].set_visible(False)
    plot_handle.spines['bottom'].set_color('gray')
    plot_handle.spines['left'].set_color('gray')

    plot_handle.xaxis.label.set_color('gray')
    plot_handle.tick_params(axis='x', colors='gray')

    plot_handle.yaxis.label.set_color('gray')
    plot_handle.tick_params(axis='y', colors='gray')
