import re

def validate_password(password: str):
    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if len(password) > 50:
        return False, "Password too long (max 50 chars)"

    # Strong password (optional but recommended)
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    return True, ""