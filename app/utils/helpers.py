import re
from datetime import datetime

def validate_phone(phone: str) -> bool:
    """Validates phone number format."""
    # Matches international format: + or digits, between 7 and 15 characters
    if not phone:
        return False
    clean_phone = re.sub(r'[\s\-()]+', '', phone)
    return bool(re.match(r'^\+?[1-9]\d{1,14}$', clean_phone))

def validate_date(date_str: str) -> bool:
    """Validates date matches YYYY-MM-DD and is not in the past."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        return dt >= datetime.today().date()
    except ValueError:
        return False

def validate_age(age_str: str) -> bool:
    """Validates age is a valid integer between 1 and 120."""
    try:
        age = int(age_str)
        return 1 <= age <= 120
    except ValueError:
        return False
