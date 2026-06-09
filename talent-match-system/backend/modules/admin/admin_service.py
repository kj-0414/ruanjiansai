from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import get_db
from modules.admin.admin_repository import AdminRepository
from utils.auth import decode_access_token
from modules.common.config import settings
import json
from datetime import datetime

class AdminService:
    def __init__(self):
        pass

    async def get_all_users(self, offset: int, limit: int, db: Session):
        repo = AdminRepository(db)
        users = repo.get_all_users(offset, limit)
        total = repo.get_user_count()

        result = []
        for user in users:
            roles = json.loads(user.roles) if user.roles else []
            result.append({
                "id": user.id,
                "phone": user.phone,
                "nickname": user.nickname,
                "roles": roles,
                "created_at": user.created_at
            })

        return {"total": total, "users": result}

    async def search_users(self, phone: str = None, role: str = None, start_date: datetime = None, end_date: datetime = None, offset: int = 0, limit: int = 10, db: Session = None):
        repo = AdminRepository(db)
        users = repo.search_users(phone, role, start_date, end_date, offset, limit)
        total = repo.search_users_count(phone, role, start_date, end_date)

        result = []
        for user in users:
            roles = json.loads(user.roles) if user.roles else []
            result.append({
                "id": user.id,
                "phone": user.phone,
                "nickname": user.nickname,
                "roles": roles,
                "created_at": user.created_at
            })

        return {"total": total, "users": result}

    async def get_user_by_id(self, user_id: str, db: Session):
        repo = AdminRepository(db)
        user = repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        roles = json.loads(user.roles) if user.roles else []
        resume_count = repo.get_user_resume_count(user_id)
        job_count = repo.get_user_job_count(user_id)
        match_count = repo.get_user_match_count(user_id)

        return {
            "id": user.id,
            "phone": user.phone,
            "nickname": user.nickname,
            "roles": roles,
            "created_at": user.created_at,
            "resume_count": resume_count,
            "job_count": job_count,
            "match_count": match_count,
            "last_active": None
        }

    async def update_user_roles(self, user_id: str, roles: list, db: Session):
        repo = AdminRepository(db)
        user = repo.update_user_roles(user_id, roles)
        if not user:
            raise ValueError("User not found")

        return {"message": "User roles updated successfully"}

    async def delete_user(self, user_id: str, db: Session):
        repo = AdminRepository(db)
        success = repo.delete_user(user_id)
        if not success:
            raise ValueError("User not found")

        return {"message": "User deleted successfully"}

    async def get_system_stats(self, db: Session):
        repo = AdminRepository(db)
        return {
            "total_users": repo.get_user_count(),
            "total_resumes": repo.get_resume_count(),
            "total_jobs": repo.get_job_count(),
            "total_matches": repo.get_match_count(),
            "job_seeker_count": repo.get_job_seeker_count(),
            "company_count": repo.get_company_count()
        }

    async def get_dashboard_summary(self, db: Session):
        repo = AdminRepository(db)
        return {
            "total_users": repo.get_user_count(),
            "total_resumes": repo.get_resume_count(),
            "total_jobs": repo.get_job_count(),
            "total_matches": repo.get_match_count(),
            "job_seeker_count": repo.get_job_seeker_count(),
            "company_count": repo.get_company_count(),
            "today_new_users": repo.get_today_new_users(),
            "today_new_resumes": repo.get_today_new_resumes(),
            "today_new_jobs": repo.get_today_new_jobs(),
            "today_matches": repo.get_today_matches()
        }

    async def get_user_trends(self, days: int = 7, db: Session = None):
        repo = AdminRepository(db)
        return {
            "user_trend": repo.get_user_trend(days),
            "resume_trend": repo.get_resume_trend(days),
            "job_trend": repo.get_job_trend(days)
        }

    async def get_system_health(self, db: Session):
        repo = AdminRepository(db)
        db_status = repo.check_database_connection()
        return {
            "status": "healthy" if db_status == "connected" else "unhealthy",
            "database": db_status,
            "api_version": settings.APP_VERSION,
            "uptime": "running",
            "database_tables": repo.get_database_stats()
        }

    async def verify_admin_role(self, token: str, db: Session):
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        repo = AdminRepository(db)
        user = repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        roles = json.loads(user.roles) if user.roles else []
        if "admin" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return {"user_id": user_id, "roles": roles}

    async def get_admin_profile(self, token: str, db: Session):
        user_info = await self.verify_admin_role(token, db)
        user_id = user_info["user_id"]

        repo = AdminRepository(db)
        user = repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("Admin not found")

        roles = json.loads(user.roles) if user.roles else []
        permissions = self._get_permissions_by_roles(roles)

        return {
            "user_id": user.id,
            "phone": user.phone,
            "roles": roles,
            "permissions": permissions
        }

    def _get_permissions_by_roles(self, roles: list) -> list:
        all_permissions = {
            "admin": ["users:read", "users:write", "users:delete", "users:role",
                     "stats:read", "health:read", "profile:read", "profile:write",
                     "resumes:read", "resumes:delete", "jobs:read", "jobs:delete",
                     "matches:read", "deliveries:read"],
            "job_seeker": ["resume:read", "resume:write", "resume:delete",
                          "job:read", "match:read"],
            "company": ["job:read", "job:write", "job:delete",
                       "resume:read", "match:read", "delivery:read"]
        }

        permissions = []
        for role in roles:
            if role in all_permissions:
                permissions.extend(all_permissions[role])
        return list(set(permissions))
