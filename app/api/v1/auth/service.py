from sqlalchemy.orm import Session
from app.models.user_model import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings


def register_user(db: Session, data):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == data.email) | (User.phone == data.phone)
    ).first()
    
    if existing_user:
        return None
    
    user = User(
        username=data.username,
        email=data.email,
        phone=data.phone,
        password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, data):
    """Login user and return JWT token"""
    user = db.query(User).filter(
        (User.email == data.email_or_phone) |
        (User.phone == data.email_or_phone)
    ).first()

    if not user:
        return None

    if not verify_password(data.password, user.password):
        return None
    
    # Create access token
    token = create_access_token(data={
        "user_id": user.id,
        "sub": user.email,
        "username": user.username
    })
    return token


def forgot_password(db, data):
    """Send OTP for password reset"""
    user = db.query(User).filter(
        (User.email == data.email_or_phone) |
        (User.phone == data.email_or_phone)
    ).first()

    if not user:
        return None

    # In production, send OTP via email/SMS
    # For demo, return fixed OTP
    return settings.OTP_CODE


def verify_otp(data):
    """Verify OTP"""
    # In production, verify against stored OTP with expiry
    if data.otp == settings.OTP_CODE:
        return True
    return False


def reset_password(db, data):
    """Reset user password"""
    user = db.query(User).filter(
        (User.email == data.email_or_phone) |
        (User.phone == data.email_or_phone)
    ).first()

    if not user:
        return None

    user.password = hash_password(data.new_password)
    db.commit()
    return True