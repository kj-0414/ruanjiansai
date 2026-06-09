from pydantic import BaseModel


class SendCodeRequest(BaseModel):
    phone: str


class RegisterRequest(BaseModel):
    phone: str
    code: str
    password: str
    nickname: str
    role: str = "job_seeker"


class LoginRequest(BaseModel):
    phone: str
    password: str
    role: str = "job_seeker"


class UserResponse(BaseModel):
    id: str
    phone: str
    nickname: str
    role: str
    roles: list


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse