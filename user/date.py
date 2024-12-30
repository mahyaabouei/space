import datetime

# تبدیل تاریخ به فرمت YYYY-MM-DD
def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date()
    except (ValueError, TypeError):
        return None