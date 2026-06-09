from pydantic import BaseModel
from typing import Optional


class JobAbilityCreate(BaseModel):
    job_id: int


class JobCreate(BaseModel):
    job_name: str
    job_desc: str
    salary: str = ""
    location: str = None
    work_hours: str = None
    education_requirement: str = None
    experience_requirement: str = None
    recruitment_count: str = None
    department: str = None
    job_type: str = None
    benefits: str = None
    responsibilities: str = None
    requirements: str = None
    skills: str = None
    education_penalty_rules: str = None
    skills_requirement: str = None
    certificate_requirements: str = None
    project_requirements: str = None
    education_level: str = None
    min_experience_years: int = None
    max_experience_years: int = None
    industry: str = None
    tech_tags: str = None
    company_name: str = None
    company_type: str = None
    company_size: str = None
    company_intro: str = None
    company_industry: str = None
    company_tags: str = None
    selected_benefits: str = None


class JobUpdate(BaseModel):
    job_name: str
    job_desc: str
    salary: str = ""
    location: str = None
    work_hours: str = None
    education_requirement: str = None
    experience_requirement: str = None
    recruitment_count: str = None
    department: str = None
    job_type: str = None
    benefits: str = None
    responsibilities: str = None
    requirements: str = None
    skills: str = None
    education_penalty_rules: str = None
    skills_requirement: str = None
    certificate_requirements: str = None
    project_requirements: str = None
    education_level: str = None
    min_experience_years: int = None
    max_experience_years: int = None
    industry: str = None
    tech_tags: str = None
    company_name: str = None
    company_type: str = None
    company_size: str = None
    company_intro: str = None
    company_industry: str = None
    company_tags: str = None
    selected_benefits: str = None