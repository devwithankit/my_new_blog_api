from app.utils.email_validator import validate_email_address
from app.utils.password_validator import validate_password
from app.utils.phone_validator import validate_phone


def validate_register_data(data):
    # Email
    is_valid, msg = validate_email_address(data.email)
    if not is_valid:
        return False, msg

    # Phone
    is_valid, msg = validate_phone(data.phone)
    if not is_valid:
        return False, msg

    # Password
    is_valid, msg = validate_password(data.password)
    if not is_valid:
        return False, msg

    return True, ""