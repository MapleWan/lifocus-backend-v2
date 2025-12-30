import re
def checkEmailFormat(email):
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_datetime_to_string(datetime, format_str = '%Y-%m-%d %H:%M:%S'):
    return datetime.strftime(format_str)