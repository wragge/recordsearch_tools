import re
import calendar
import datetime

def process_date(date_string):
    month_names = dict((v,k) for k,v in enumerate(calendar.month_name))
    month_abbrs = dict((v,k) for k,v in enumerate(calendar.month_abbr))
    dates = date_string.split('-')
    results = []
    for this_date in dates:
        try:
            day, month_name, year = re.search(r'(\d{0,2})\s*([A-Za-z]*)\s*(\d{4})', this_date).groups()
        except AttributeError:
            # It's a non-standard date so return nothing and worry about it later
            return [(None, 0, 0, 0)]
        try:
            month = month_names[month_name]
        except KeyError:
            try:
                month = month_abbrs[month_name]
            except KeyError:
                month = None
        day = int(day) if day else 0
        month = int(month) if month else 0
        year = int(year) if year else 0
        if day and month and year:
            try:
                new_date = datetime.date(year, month, day)
            except ValueError:
                new_date = None
        else:
            new_date = None
        results.append((new_date, day, month, year))
    return results