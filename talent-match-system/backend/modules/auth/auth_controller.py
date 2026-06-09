from fastapi import APIRouter, Depends, HTTPException, status
from modules.auth.auth_service import AuthService
from modules.auth.schemas import SendCodeRequest, RegisterRequest, LoginRequest
from modules.auth.exceptions import (
    InvalidPhoneException,
    InvalidCodeException,
    PhoneAlreadyRegisteredException,
    AuthenticationFailedException,
    UserNotFoundException
)
from utils.auth import get_current_user
from models import get_db
from sqlalchemy.orm import Session

router = APIRouter()
auth_service = AuthService()


@router.post("/send-code")
async def send_code(request: SendCodeRequest):
    try:
        return auth_service.send_code(request)
    except InvalidPhoneException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.register(request, db)
    except InvalidPhoneException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidCodeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PhoneAlreadyRegisteredException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.login(request, db)
    except InvalidPhoneException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthenticationFailedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = current_user.get("user_id")
        return auth_service.get_user_info(user_id, db)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return auth_service.logout()