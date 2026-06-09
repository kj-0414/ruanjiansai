from pydantic import BaseModel
from typing import Optional


class ResumeUpdate(BaseModel):
    resume_name: str
    name: str = "未知"
    age: Optional[int] = None
    phone: str = ""
    email: str = ""
    desired_position: str = ""
    address: str = ""
    education: str = ""
    school: str = ""
    major: str = ""
    degree: str = "不限"
    graduation_date: str = ""
    skills: str = "[]"
    self_evaluation: str = ""
    certificates: str = "[]"
    projects: str = "[]"
    work_experience: str = "[]"
    internship_experience: str = "[]"
    experiences: str = "[]"
    honors: str = "[]"
    desired_salary: str = ""
    work_years: int = 0


class ResumeResponse(BaseModel):
    id: int
    resume_name: str
    filename: str
    filepath: str
    user_id: str
    name: str
    age: Optional[int] = None
    phone: str
    email: str
    desired_position: str
    address: str
    education: str
    school: str
    major: str
    degree: str
    graduation_date: str = ""
    experience: str
    skills: list
    skill_tags: dict = {}
    self_evaluation: str
    certificates: list
    projects: list
    work_experience: list
    internship_experience: list = []
    skills_detail: list
    desired_salary: str
    work_years: int
    create_time: str