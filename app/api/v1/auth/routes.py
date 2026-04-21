from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_schema import (
    RegisterSchema, LoginSchema, ForgotPasswordSchema, 
    VerifyOTPSchema, ResetPasswordSchema
)
from app.api.v1.auth.service import (
    register_user, login_user, forgot_password, verify_otp, reset_password
)
from app.db.session import get_db
from app.utils.response import SuccessResponse, ErrorResponse
from app.dependencies.api_key_dependency import verify_api_keys
from app.utils.user_validator import validate_register_data

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    dependencies=[Depends(verify_api_keys)]
)

@router.post("/register", summary="User Registration")
def register_user_endpoint(data: RegisterSchema, db: Session = Depends(get_db)):

    # ✅ VALIDATION
    is_valid, msg = validate_register_data(data)
    if not is_valid:
        return ErrorResponse(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    user = register_user(db, data)

    if not user:
        return ErrorResponse(
            message="User already exists with this email or phone",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    return SuccessResponse(
        message="User registered successfully",
        status_code=status.HTTP_201_CREATED,
        data={
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone
        }
    )

@router.post("/login")
def login_user_endpoint(data: LoginSchema, db: Session = Depends(get_db)):

    if not data.email_or_phone or not data.password:
        return ErrorResponse(
            message="Email/Phone and password required",
            status_code=400
        )

    token = login_user(db, data)

    if not token:
        return ErrorResponse(
            message="Invalid credentials",
            status_code=401
        )

    return SuccessResponse(
        message="Login successful",
        status_code=200,
        data={
            "access_token": token,
            "token_type": "bearer"
        }
    )

@router.post("/forgot-password", summary="Forgot Password", description="Request OTP for password reset")
def forgot_password_endpoint(data: ForgotPasswordSchema, db: Session = Depends(get_db)):
    """Request OTP for password reset"""
    otp = forgot_password(db, data)

    if not otp:
        return ErrorResponse(
            message="User not found with this email/phone", 
            status_code=status.HTTP_404_NOT_FOUND
        )

    return SuccessResponse(
        message="OTP sent successfully", 
        status_code=status.HTTP_200_OK,
        data={"otp": otp}  # In production, don't return OTP in response
    )


@router.post("/verify-otp", summary="Verify OTP", description="Verify OTP for password reset")
def verify_otp_endpoint(data: VerifyOTPSchema):
    """Verify OTP code"""
    if not verify_otp(data):
        return ErrorResponse(
            message="Invalid OTP", 
            status_code=status.HTTP_400_BAD_REQUEST
        )

    return SuccessResponse(
        message="OTP verified successfully", 
        status_code=status.HTTP_200_OK,
        data={"verified": True}
    )


@router.post("/reset-password", summary="Reset Password", description="Reset password after OTP verification")
def reset_password_endpoint(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    """Reset user password"""
    result = reset_password(db, data)

    if not result:
        return ErrorResponse(
            message="User not found", 
            status_code=status.HTTP_404_NOT_FOUND
        )

    return SuccessResponse(
        message="Password updated successfully", 
        status_code=status.HTTP_200_OK
    )