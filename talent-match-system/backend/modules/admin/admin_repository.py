from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from models import User, Resume, Job, Match, Delivery, AIResumeParse, AbilityAnalysisCache
from datetime import datetime, timedelta
import json

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self, offset: int = 0, limit: int = 10):
        return self.db.query(User).order_by(desc(User.created_at)).offset(offset).limit(limit).all()

    def get_user_count(self):
        return self.db.query(User).count()

    def get_user_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_phone(self, phone: str):
        return self.db.query(User).filter(User.phone == phone).first()

    def search_users(self, phone: str = None, role: str = None, start_date: datetime = None, end_date: datetime = None, offset: int = 0, limit: int = 10):
        query = self.db.query(User)
        if phone:
            query = query.filter(User.phone.like(f"%{phone}%"))
        if start_date:
            query = query.filter(User.created_at >= start_date)
        if end_date:
            query = query.filter(User.created_at <= end_date)
        users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
        if role:
            users = [u for u in users if role in (json.loads(u.roles) if u.roles else [])]
        return users

    def search_users_count(self, phone: str = None, role: str = None, start_date: datetime = None, end_date: datetime = None):
        query = self.db.query(func.count(User.id))
        if phone:
            query = query.filter(User.phone.like(f"%{phone}%"))
        if start_date:
            query = query.filter(User.created_at >= start_date)
        if end_date:
            query = query.filter(User.created_at <= end_date)
        return query.scalar()

    def update_user_roles(self, user_id: str, roles: list):
        user = self.get_user_by_id(user_id)
        if user:
            user.roles = json.dumps(roles)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: str):
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def get_resume_count(self):
        return self.db.query(Resume).count()

    def get_job_count(self):
        return self.db.query(Job).count()

    def get_match_count(self):
        return self.db.query(Match).count()

    def get_job_seeker_count(self):
        result = self.db.query(
            func.count(User.id)
        ).filter(
            User.roles.like('%job_seeker%')
        ).scalar()
        return result or 0

    def get_company_count(self):
        result = self.db.query(
            func.count(User.id)
        ).filter(
            User.roles.like('%company%')
        ).scalar()
        return result or 0

    def get_user_resume_count(self, user_id: str):
        return self.db.query(Resume).filter(Resume.user_id == user_id).count()

    def get_user_job_count(self, user_id: str):
        return self.db.query(Job).filter(Job.user_id == user_id).count()

    def get_user_match_count(self, user_id: str):
        resume_ids = [r.id for r in self.db.query(Resume.id).filter(Resume.user_id == user_id).all()]
        if not resume_ids:
            return 0
        return self.db.query(Match).filter(Match.resume_id.in_(resume_ids)).count()

    def get_today_new_users(self):
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.db.query(func.count(User.id)).filter(User.created_at >= today_start).scalar() or 0

    def get_today_new_resumes(self):
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.db.query(func.count(Resume.id)).filter(Resume.created_at >= today_start).scalar() or 0

    def get_today_new_jobs(self):
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.db.query(func.count(Job.id)).filter(Job.created_at >= today_start).scalar() or 0

    def get_today_matches(self):
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.db.query(func.count(Match.id)).filter(Match.created_at >= today_start).scalar() or 0

    def get_user_trend(self, days: int = 7):
        trends = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            date_start = datetime.combine(date, datetime.min.time())
            date_end = datetime.combine(date, datetime.max.time())
            count = self.db.query(func.count(User.id)).filter(
                and_(User.created_at >= date_start, User.created_at <= date_end)
            ).scalar() or 0
            trends.append({"date": date.strftime("%Y-%m-%d"), "count": count})
        return list(reversed(trends))

    def get_resume_trend(self, days: int = 7):
        trends = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            date_start = datetime.combine(date, datetime.min.time())
            date_end = datetime.combine(date, datetime.max.time())
            count = self.db.query(func.count(Resume.id)).filter(
                and_(Resume.created_at >= date_start, Resume.created_at <= date_end)
            ).scalar() or 0
            trends.append({"date": date.strftime("%Y-%m-%d"), "count": count})
        return list(reversed(trends))

    def get_job_trend(self, days: int = 7):
        trends = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            date_start = datetime.combine(date, datetime.min.time())
            date_end = datetime.combine(date, datetime.max.time())
            count = self.db.query(func.count(Job.id)).filter(
                and_(Job.created_at >= date_start, Job.created_at <= date_end)
            ).scalar() or 0
            trends.append({"date": date.strftime("%Y-%m-%d"), "count": count})
        return list(reversed(trends))

    def get_database_stats(self):
        return {
            "users": self.get_user_count(),
            "resumes": self.get_resume_count(),
            "jobs": self.get_job_count(),
            "matches": self.get_match_count(),
            "deliveries": self.db.query(Delivery).count(),
            "ai_resume_parse": self.db.query(AIResumeParse).count(),
            "ability_cache": self.db.query(AbilityAnalysisCache).count(),
        }

    def check_database_connection(self):
        try:
            self.db.query(func.count()).select_from(User).scalar()
            return "connected"
        except Exception:
            return "disconnected"
