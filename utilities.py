import re
import calendar
import datetime


def parse_date(date_string):
    date_obj = None
    day = False
    month = False
    date_formats = [('%d %B %Y', True, True),
                    ('%d %b %Y', True, True),
                    ('%d %b. %Y', True, True),
                    ('%B %Y', False, True),
                    ('%b %Y', False, True),
                    ('%Y', False, False),
                    ]
    for date_format in date_formats:
        try:
            date_obj = datetime.datetime.strptime(date_string, date_format[0])
        except ValueError:
            pass
        else:
            day = date_format[1]
            month = date_format[2]
            break
    return {'date': date_obj, 'day': day, 'month': month}


def process_date_string(date_string):
    '''
    Takes a date range in a string and returns date objects,
    and booleans indicating if values for month and day exist.
    '''
    dates = date_string.split('-')
    results = []
    for this_date in dates:
        results.append(parse_date(this_date.strip()))
    return results


def convert_date_to_iso(date_dict):
    '''
    Simple ISO date formatting.
    Not dependent on strftime and its year limits.
    '''
    date_obj = date_dict['date']
    if date_obj:
        if date_dict['day']:
            iso_date = '{0.year}-{0.month:02d}-{0.day:02d}'.format(date_obj)
        elif date_dict['month']:
            iso_date = '{0.year}-{0.month:02d}'.format(date_obj)
        else:
            iso_date = '{0.year}'.format(date_obj)
    else:
        iso_date = None
    return iso_date
