from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from models import get_db
from modules.admin.admin_service import AdminService
from modules.admin.admin_repository import AdminRepository
from modules.admin.schemas import (
    UserListResponse, SystemStatsResponse, RoleUpdateRequest,
    UserDetailResponse, DashboardSummary, UserTrendResponse, SystemHealthResponse, AdminProfileResponse
)
from fastapi.security import OAuth2PasswordBearer
import json
from datetime import datetime

router = APIRouter()
admin_service = AdminService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return await admin_service.verify_admin_role(token, db)

@router.get("/users", response_model=UserListResponse)
async def get_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        return await admin_service.get_all_users(offset, limit, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users/search", response_model=UserListResponse)
async def search_users(
    phone: str = Query(None, description="手机号模糊搜索"),
    role: str = Query(None, description="角色筛选"),
    start_date: datetime = Query(None, description="注册起始日期"),
    end_date: datetime = Query(None, description="注册结束日期"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        return await admin_service.search_users(phone, role, start_date, end_date, offset, limit, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        return await admin_service.get_user_by_id(user_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/users/{user_id}/roles")
async def update_user_roles(
    user_id: str,
    request: RoleUpdateRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        return await admin_service.update_user_roles(user_id, request.roles, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        return await admin_service.delete_user(user_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return await admin_service.get_system_stats(db)

@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return await admin_service.get_dashboard_summary(db)

@router.get("/trends", response_model=UserTrendResponse)
async def get_user_trends(
    days: int = Query(7, ge=1, le=30, description="趋势天数"),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return await admin_service.get_user_trends(days, db)

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return await admin_service.get_system_health(db)

@router.get("/profile", response_model=AdminProfileResponse)
async def get_admin_profile(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        return await admin_service.get_admin_profile(token, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/users/{user_id}/promote")
async def promote_to_admin(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        repo = AdminRepository(db)
        user = repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        roles = json.loads(user.roles) if user.roles else []
        if "admin" not in roles:
            roles.append("admin")
            await admin_service.update_user_roles(user_id, roles, db)

        return {"message": "User promoted to admin successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/status")
async def admin_health():
    return {"status": "admin service healthy"}