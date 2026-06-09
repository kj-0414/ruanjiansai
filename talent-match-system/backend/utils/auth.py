from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from modules.common.config import settings
from models import get_db
from models import User as UserModel
from sqlalchemy.orm import Session
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        db = next(get_db())
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if user:
            roles = json.loads(user.roles) if user.roles else []
            role = roles[0] if roles else ""
            return {"user_id": user_id, "role": role}
        
        return {"user_id": user_id, "role": ""}
    except JWTError:
        raise credentials_exception

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": user_id}
    except JWTError:
        return None

def get_role(request: Request):
    role = request.headers.get("X-Role")
    if not role:
        return "job_seeker"
    return role

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
        user = db.query(UserModel).filter(UserModel.id == current_user["user_id"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        roles = json.loads(user.roles) if user.roles else []
        if not any(role in self.allowed_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        return current_user

def require_role(required_role: str):
    async def role_checker(request: Request, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
        user = db.query(UserModel).filter(UserModel.id == current_user["user_id"]).first()
        if not user:
            print(f"[Role Check] User not found: {current_user['user_id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        roles = json.loads(user.roles) if user.roles else []
        if required_role not in roles:
            print(f"[Role Check] User {current_user['user_id']} has roles {roles}, but requires {required_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Requires role: {required_role}"
            )
        
        print(f"[Role Check] Role check passed for user: {current_user['user_id']}")
        return current_user
    return role_checker