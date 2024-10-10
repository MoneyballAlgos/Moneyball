import calendar
from datetime import datetime, timedelta
from django.utils.html import format_html

def colour(value):
    if value == 0:
        return value
    elif value < 0:
        return format_html('<strong style="color:Red;">{}</strong>', value)
    return format_html('<strong style="color:Green;">{}</strong>', value)


def calculate_volatility(dt):
    dt['Return'] = 100 * (dt['Close'].pct_change())
    daily_volatility = dt['Return'].std()
    return daily_volatility


def colour_indicator(obj, price):
    diff = price - obj.price
    profit = round(((diff/obj.price) * 100), 2)
    if profit < 0:
      return format_html('<strong style="color:Red;">{}</strong>', profit)
    return format_html('<strong style="color:Green;">{}</strong>', profit)


def last_thursday(now):
    # Get the last day of the month
    last_day = calendar.monthrange(now.date().year, now.date().month)[1]
    
    # Create a date object for the last day of the month
    last_date = datetime(now.date().year, now.date().month, last_day)
    
    # Find the last Thursday
    while last_date.weekday() != calendar.THURSDAY:
        last_date -= timedelta(days=1)
        
    return last_date

def next_multiple_of_5_after_decimal(num):
    # Get the decimal part, int value
    decimal_part = num - int(num)
    int_num = num - decimal_part
    
    if decimal_part == 0.0:
        return num
    
    # Convert the decimal part to an integer in terms of tenths, hundredths, etc.
    decimal_as_int = int(decimal_part * 100)  # 2 decimal places

    # Check the next multiples of 5
    for i in range(decimal_as_int + 1, 100):  # Up to 1.00 (i.e., 100)
        if i % 5 == 0:
            return int_num + i / 100.0  # Return the result as a float

    return None  # In case there's no valid multiple found
