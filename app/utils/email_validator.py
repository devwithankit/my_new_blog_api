from email_validator import validate_email, EmailNotValidError

def validate_email_address(email: str):
    try:
        validate_email(email)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)