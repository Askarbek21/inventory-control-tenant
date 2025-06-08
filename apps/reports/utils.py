from django.utils.dateparse import parse_datetime
from django.utils.timezone import now, timedelta


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

    return date_from, date_to
