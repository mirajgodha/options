import datetime


def get_expiry_date(year, month):
    # Pass year as 2024
    # Pass month as JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC

    # Convert month abbreviation to corresponding month number
    month_number = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
        'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
        'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }[month.upper()]

    # Get the last day of the given month
    last_day = datetime.date(int(year), month_number, 1) + datetime.timedelta(days=32)
    last_day = last_day.replace(day=1) - datetime.timedelta(days=1)

    # Find the weekday of the last day
    weekday = last_day.weekday()

    # Calculate the number of days to subtract to reach Thursday (weekday 3)
    days_to_subtract = (weekday - 3) % 7

    # Calculate the last Thursday
    last_thursday = last_day - datetime.timedelta(days=days_to_subtract)

    return last_thursday