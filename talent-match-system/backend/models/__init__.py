from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from modules.common import get_settings
import os

# 添加达梦数据库 bin 目录到 PATH
os.environ['PATH'] = 'D:\\dm8\\bin;' + os.environ.get('PATH', '')

settings = get_settings()

# 注册达梦数据库方言
try:
    import dpi
    from sqlalchemy.dialects import registry
    import dmSQLAlchemy
    registry.register('dm', 'dmSQLAlchemy.dmPython', 'DMDialect_dmPython')
    registry.register('dm.dmPython', 'dmSQLAlchemy.dmPython', 'DMDialect_dmPython')
    print('OK dmSQLAlchemy dialect registered')
except Exception as e:
    print(f'WARN: Could not register dm dialect: {e}')

# 数据库配置
engine = create_engine(
    settings.database_url,
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    roles = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String)
    age = Column("candidate_age", Integer)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    education = Column(String)
    school = Column(String)
    major = Column(String)
    degree = Column(String)
    graduation_date = Column("grad_date", String)
    experience = Column(String)
    skills = Column(Text)
    self_evaluation = Column(Text)
    created_at = Column(DateTime, nullable=False)
    
    # 保留旧字段以兼容已有数据
    work_experience = Column(Text)
    projects = Column(Text)
    certificates = Column(Text)
    skills_detail = Column(Text)
    internship_experience = Column(Text)
    
    # 新字段
    experiences = Column(Text)  # 统一实践经历（工作/实习/项目）
    honors = Column(Text)        # 获奖荣誉
    desired_salary = Column(String)
    work_years = Column(Integer)
    desired_position = Column(String)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_name = Column(String, nullable=False)
    job_desc = Column(Text, nullable=False)
    salary = Column(String, nullable=False)
    location = Column(String)
    work_hours = Column(String)
    education_requirement = Column(String)
    experience_requirement = Column(String)
    recruitment_count = Column(String)
    department = Column(String)
    job_type = Column(String)
    benefits = Column(Text)
    responsibilities = Column(Text)
    requirements = Column(Text)
    skills = Column(Text)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    skills_requirement = Column(Text)
    certificate_requirements = Column(Text)
    project_requirements = Column(Text)
    education_level = Column(String)
    min_experience_years = Column(Integer)
    max_experience_years = Column(Integer)
    industry = Column(String)
    tech_tags = Column(Text)
    education_penalty_rules = Column(Text)
    
    company_name = Column(String)
    company_type = Column(String)
    company_size = Column(String)
    company_intro = Column(Text)
    company_industry = Column(String)
    company_tags = Column(Text)
    selected_benefits = Column(Text)

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score = Column(Integer, nullable=False)
    match_tags = Column(Text)
    gap_tags = Column(Text)
    ability_graph = Column(Text)
    created_at = Column(DateTime, nullable=False)

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

class JobFavorite(Base):
    __tablename__ = "job_favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_seeker_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_conversation_status', 'status'),
        Index('idx_job_seeker_company', 'job_seeker_id', 'company_id'),
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_conversation_id', 'conversation_id'),
        Index('idx_sender_id', 'sender_id'),
        Index('idx_receiver_id', 'receiver_id'),
        Index('idx_created_at', 'created_at'),
    )

class SystemMessageTemplate(Base):
    __tablename__ = "system_message_templates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    template_content = Column(Text, nullable=False)
    description = Column(String)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_is_active', 'is_active'),
    )

class SystemMessage(Base):
    __tablename__ = "system_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("system_message_templates.id"))
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    is_read = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_category', 'category'),
        Index('idx_is_read', 'is_read'),
        Index('idx_created_at', 'created_at'),
    )

class MessageStatus(Base):
    __tablename__ = "message_status"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(Text)
    updated_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_message_id', 'message_id'),
        Index('idx_status', 'status'),
    )

class AIResumeParse(Base):
    __tablename__ = "ai_resume_parse"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_result = Column(Text, nullable=False)
    skills = Column(Text)
    experience = Column(Text)
    education = Column(Text)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    parse_status = Column(String, nullable=False, default="pending")
    is_manual_modified = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    certificates = Column(Text)
    projects = Column(Text)
    work_experience = Column(Text)
    skills_detail = Column(Text)
    internship_experience = Column(Text)

class AIJobParse(Base):
    __tablename__ = "ai_job_parse"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_result = Column(Text, nullable=False)
    required_skills = Column(Text)
    job_requirements = Column(Text)
    salary_range = Column(String)
    job_title = Column(String)
    parse_status = Column(String, nullable=False, default="pending")
    is_manual_modified = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    certificate_requirements = Column(Text)
    project_requirements = Column(Text)
    skills_requirement = Column(Text)
    education_level = Column(String)
    industry = Column(String)
    tech_tags = Column(Text)

class AbilityAnalysisCache(Base):
    __tablename__ = "ability_analysis_cache"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    analysis_type = Column(String, nullable=False)
    result = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_user_analysis_type', 'user_id', 'analysis_type'),
    )

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("数据库表创建成功！")