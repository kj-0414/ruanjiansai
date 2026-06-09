from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from utils.auth import create_access_token
from modules.common.config import settings
from modules.auth.auth_repository import AuthRepository
from modules.auth.schemas import SendCodeRequest, RegisterRequest, LoginRequest
from modules.auth.exceptions import (
    InvalidPhoneException,
    InvalidCodeException,
    PhoneAlreadyRegisteredException,
    AuthenticationFailedException,
    UserNotFoundException
)
from sqlalchemy.orm import Session
import random
import json


verification_codes = {}


class AuthService:
    def __init__(self):
        self.repository = None

    def _init_repository(self, db: Session):
        if not self.repository:
            self.repository = AuthRepository(db)

    def _validate_phone(self, phone: str):
        if not phone or len(phone) != 11 or not phone.isdigit():
            raise InvalidPhoneException("Invalid phone number format")

    def send_code(self, request: SendCodeRequest) -> dict:
        self._validate_phone(request.phone)
        
        code = str(random.randint(100000, 999999))
        verification_codes[request.phone] = code
        
        print(f"[验证码] 手机号: {request.phone}, 验证码: {code}")
        
        return {"message": "Verification code sent", "code": code}

    def register(self, request: RegisterRequest, db: Session) -> dict:
        self._init_repository(db)
        self._validate_phone(request.phone)
        
        if request.phone not in verification_codes or verification_codes[request.phone] != request.code:
            raise InvalidCodeException("Invalid verification code")
        
        allowed_roles = ["job_seeker", "company"]
        if request.role not in allowed_roles:
            raise InvalidPhoneException(f"Invalid role. Allowed roles: {allowed_roles}")
        
        existing_user = self.repository.get_user_by_phone_and_role(request.phone, request.role)
        if existing_user:
            role_name = "求职者" if request.role == "job_seeker" else "企业"
            raise PhoneAlreadyRegisteredException(f"该手机号已注册为{role_name}账号")
        
        hashed_password = generate_password_hash(request.password)
        new_user = self.repository.create_user(request.phone, hashed_password, request.nickname, request.role)
        
        del verification_codes[request.phone]
        
        return {"message": "User registered successfully", "user_id": new_user.id}

    def login(self, request: LoginRequest, db: Session) -> dict:
        self._init_repository(db)
        self._validate_phone(request.phone)
        
        print(f"[DEBUG] Login attempt - Phone: {request.phone}, Role: {request.role}")
        print(f"[DEBUG] Login attempt - Password received: '{request.password}'")
        
        user = self.repository.get_user_by_phone_and_role(request.phone, request.role)
        if not user:
            role_name = "求职者" if request.role == "job_seeker" else "企业"
            print(f"[DEBUG] User not found for phone: {request.phone} with role: {role_name}")
            raise AuthenticationFailedException(f"该手机号未注册为{role_name}账号")
        
        print(f"[DEBUG] User found: {user.phone}")
        print(f"[DEBUG] Stored password hash: {user.password[:50]}...")
        
        password_match = check_password_hash(user.password, request.password)
        print(f"[DEBUG] Password match: {password_match}")
        
        if not password_match:
            print(f"[DEBUG] Password verification failed")
            raise AuthenticationFailedException("密码错误")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        roles = json.loads(user.roles) if user.roles else []
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "phone": user.phone,
                "nickname": user.nickname,
                "role": roles[0] if roles else request.role,
                "roles": roles if roles else [request.role]
            }
        }

    def get_user_info(self, user_id: str, db: Session) -> dict:
        self._init_repository(db)
        
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")
        
        roles = json.loads(user.roles) if user.roles else []
        
        return {
            "id": user.id,
            "phone": user.phone,
            "nickname": user.nickname,
            "role": roles[0] if roles else "job_seeker",
            "roles": roles if roles else ["job_seeker"]
        }

    def logout(self):
        return {"message": "Logout successful"}