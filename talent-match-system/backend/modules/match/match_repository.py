from sqlalchemy.orm import Session
from models import Match as MatchModel, Resume as ResumeModel, Job as JobModel, Delivery as DeliveryModel
from datetime import datetime
import json


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_match_by_id(self, match_id: int) -> MatchModel:
        return self.db.query(MatchModel).filter(MatchModel.id == match_id).first()

    def get_matches_by_resume(self, resume_id: int) -> list:
        return self.db.query(MatchModel).filter(MatchModel.resume_id == resume_id).all()

    def get_matches_by_job(self, job_id: int) -> list:
        return self.db.query(MatchModel).filter(MatchModel.job_id == job_id).all()

    def get_all_matches(self) -> list:
        return self.db.query(MatchModel).order_by(MatchModel.match_score.desc()).all()

    def create_match(self, data: dict) -> MatchModel:
        new_match = MatchModel(
            resume_id=data.get("resume_id"),
            job_id=data.get("job_id"),
            match_score=data.get("match_score", 0),
            match_tags=data.get("match_tags", "[]"),
            gap_tags=data.get("gap_tags", "[]"),
            ability_graph=data.get("ability_graph", "{}"),
            created_at=datetime.now()
        )
        self.db.add(new_match)
        self.db.commit()
        self.db.refresh(new_match)
        return new_match

    def update_match(self, match_id: int, data: dict) -> MatchModel:
        match = self.get_match_by_id(match_id)
        if match:
            for key, value in data.items():
                setattr(match, key, value)
            self.db.commit()
            self.db.refresh(match)
        return match

    def delete_match(self, match_id: int) -> bool:
        match = self.get_match_by_id(match_id)
        if not match:
            return False
        self.db.delete(match)
        self.db.commit()
        return True

    def get_resume(self, resume_id: int) -> ResumeModel:
        return self.db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()

    def get_job(self, job_id: int) -> JobModel:
        return self.db.query(JobModel).filter(JobModel.id == job_id).first()

    def get_resumes_by_user(self, user_id: str) -> list:
        return self.db.query(ResumeModel).filter(ResumeModel.user_id == user_id).all()

    def get_jobs_by_user(self, user_id: str) -> list:
        return self.db.query(JobModel).filter(JobModel.user_id == user_id).all()

    def get_delivery(self, resume_id: int, job_id: int) -> DeliveryModel:
        return self.db.query(DeliveryModel).filter(
            DeliveryModel.resume_id == resume_id,
            DeliveryModel.job_id == job_id
        ).first()

    def create_delivery(self, data: dict) -> DeliveryModel:
        new_delivery = DeliveryModel(
            resume_id=data.get("resume_id"),
            job_id=data.get("job_id"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now())
        )
        self.db.add(new_delivery)
        self.db.commit()
        self.db.refresh(new_delivery)
        return new_delivery