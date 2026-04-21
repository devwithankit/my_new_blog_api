from pydantic import BaseModel

class RegisterSchema(BaseModel):
    username: str
    email: str
    phone: str
    password: str

class LoginSchema(BaseModel):
    email_or_phone: str
    password: str

class ForgotPasswordSchema(BaseModel):
    email_or_phone: str


class VerifyOTPSchema(BaseModel):
    email_or_phone: str
    otp: str


class ResetPasswordSchema(BaseModel):
    email_or_phone: str
    new_password: str