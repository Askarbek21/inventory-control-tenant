from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime

def get_date_range_with_period(request, default_period="day"):
    today = now()
    period = request.query_params.get("period", default_period)

    if period == 'week':
        default_start = today - timedelta(days=7)
    elif period == 'month':
        default_start = today - timedelta(days=30)
    else:
        default_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

    date_from_str = request.query_params.get("date_from")
    date_to_str = request.query_params.get("date_to")

    date_from = parse_datetime(date_from_str) if date_from_str else default_start
    date_to = parse_datetime(date_to_str) if date_to_str else today

    if date_to and date_to.time() == datetime.min.time():
        date_to = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)

    return date_from, date_to

