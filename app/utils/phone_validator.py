import re

def validate_phone(phone: str):
    pattern = r"^[6-9]\d{9}$"
    if not re.match(pattern, phone):
        return False, "Invalid phone number format"
    return True, ""