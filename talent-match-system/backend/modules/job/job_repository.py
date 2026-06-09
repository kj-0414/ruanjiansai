from sqlalchemy.orm import Session
from models import Job as JobModel, Match, Delivery, JobFavorite, Conversation, AIJobParse
from datetime import datetime
import os


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_job_by_id(self, job_id: int) -> JobModel:
        return self.db.query(JobModel).filter(JobModel.id == job_id).first()

    def get_jobs_by_user(self, user_id: str) -> list:
        return self.db.query(JobModel).filter(JobModel.user_id == user_id).all()

    def get_all_jobs(self) -> list:
        return self.db.query(JobModel).all()

    def create_job(self, data: dict) -> JobModel:
        new_job = JobModel(
            job_name=data.get("job_name"),
            job_desc=data.get("job_desc"),
            salary=data.get("salary", ""),
            location=data.get("location", ""),
            work_hours=data.get("work_hours", ""),
            education_requirement=data.get("education_requirement", ""),
            experience_requirement=data.get("experience_requirement", ""),
            recruitment_count=data.get("recruitment_count", ""),
            department=data.get("department", ""),
            job_type=data.get("job_type", ""),
            benefits=data.get("benefits", ""),
            responsibilities=data.get("responsibilities", ""),
            requirements=data.get("requirements", ""),
            skills=data.get("skills", ""),
            education_penalty_rules=data.get("education_penalty_rules", ""),
            skills_requirement=data.get("skills_requirement", ""),
            certificate_requirements=data.get("certificate_requirements", ""),
            project_requirements=data.get("project_requirements", ""),
            education_level=data.get("education_level", ""),
            min_experience_years=data.get("min_experience_years", 0),
            max_experience_years=data.get("max_experience_years", 0),
            industry=data.get("industry", ""),
            tech_tags=data.get("tech_tags", ""),
            company_name=data.get("company_name", ""),
            company_type=data.get("company_type", ""),
            company_size=data.get("company_size", ""),
            company_intro=data.get("company_intro", ""),
            company_industry=data.get("company_industry", ""),
            company_tags=data.get("company_tags", ""),
            selected_benefits=data.get("selected_benefits", ""),
            user_id=data.get("user_id"),
            created_at=datetime.now()
        )
        self.db.add(new_job)
        self.db.commit()
        self.db.refresh(new_job)
        return new_job

    def update_job(self, job_id: int, data: dict) -> JobModel:
        job = self.get_job_by_id(job_id)
        if job:
            for key, value in data.items():
                setattr(job, key, value)
            self.db.commit()
            self.db.refresh(job)
        return job

    def delete_job(self, job_id: int) -> bool:
        job = self.get_job_by_id(job_id)
        if not job:
            return False

        self.db.query(Match).filter(Match.job_id == job_id).delete()
        self.db.query(Delivery).filter(Delivery.job_id == job_id).delete()
        self.db.query(JobFavorite).filter(JobFavorite.job_id == job_id).delete()
        self.db.query(Conversation).filter(Conversation.job_id == job_id).delete()
        self.db.query(AIJobParse).filter(AIJobParse.job_id == job_id).delete()
        
        self.db.commit()
        self.db.delete(job)
        self.db.commit()
        return True