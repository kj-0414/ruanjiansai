from sqlalchemy.orm import Session
from models import Resume as ResumeModel, Match, Delivery, AIResumeParse, Conversation, AbilityAnalysisCache, Message
from datetime import datetime
import os


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_resume_by_id(self, resume_id: int) -> ResumeModel:
        return self.db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()

    def get_resumes_by_user(self, user_id: str) -> list:
        return self.db.query(ResumeModel).filter(ResumeModel.user_id == user_id).all()

    def get_all_resumes(self) -> list:
        return self.db.query(ResumeModel).all()

    def create_resume(self, data: dict) -> ResumeModel:
        print(f"[DEBUG] create_resume接收的data:", data)
        print(f"[DEBUG] data中的experiences:", data.get("experiences"))
        print(f"[DEBUG] data中的honors:", data.get("honors"))
        
        new_resume = ResumeModel(
            resume_name=data.get("resume_name"),
            filename=data.get("filename"),
            filepath=data.get("filepath"),
            user_id=data.get("user_id"),
            name=data.get("name", "未知"),
            age=data.get("age"),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            desired_position=data.get("desired_position", ""),
            address=data.get("address", ""),
            education=data.get("education", ""),
            school=data.get("school", ""),
            major=data.get("major", ""),
            degree=data.get("degree", "不限"),
            graduation_date=data.get("graduation_date", ""),
            experience=data.get("experience", "未知"),
            skills=data.get("skills", "[]"),
            self_evaluation=data.get("self_evaluation", ""),
            certificates=data.get("certificates", "[]"),
            projects=data.get("projects", "[]"),
            work_experience=data.get("work_experience", "[]"),
            internship_experience=data.get("internship_experience", "[]"),
            skills_detail=data.get("skills_detail", "[]"),
            desired_salary=data.get("desired_salary", ""),
            work_years=data.get("work_years", 0),
            experiences=data.get("experiences", "[]"),
            honors=data.get("honors", "[]"),
            created_at=datetime.now()
        )
        print(f"[DEBUG] 创建的ResumeModel: {new_resume.experiences}, {new_resume.honors}")
        self.db.add(new_resume)
        self.db.commit()
        self.db.refresh(new_resume)
        print(f"[DEBUG] commit后ResumeModel: {new_resume.experiences}, {new_resume.honors}")
        return new_resume

    def update_resume(self, resume_id: int, data: dict) -> ResumeModel:
        resume = self.get_resume_by_id(resume_id)
        if resume:
            for key, value in data.items():
                setattr(resume, key, value)
            self.db.commit()
            self.db.refresh(resume)
        return resume

    def delete_resume(self, resume_id: int) -> bool:
        resume = self.get_resume_by_id(resume_id)
        if not resume:
            return False
        
        # 保存文件路径用于后续删除
        filepath = resume.filepath
        
        try:
            # 删除所有关联记录（外键约束要求先删除子表记录）
            # 1. 获取所有关联的对话ID
            conversation_ids = [c.id for c in self.db.query(Conversation.id).filter(Conversation.resume_id == resume_id).all()]
            
            # 2. 删除消息记录（依赖对话）
            if conversation_ids:
                self.db.query(Message).filter(Message.conversation_id.in_(conversation_ids)).delete(synchronize_session=False)
            
            # 3. 删除能力分析缓存
            self.db.query(AbilityAnalysisCache).filter(AbilityAnalysisCache.resume_id == resume_id).delete(synchronize_session=False)
            
            # 4. 删除AI简历解析
            self.db.query(AIResumeParse).filter(AIResumeParse.resume_id == resume_id).delete(synchronize_session=False)
            
            # 5. 删除投递记录
            self.db.query(Delivery).filter(Delivery.resume_id == resume_id).delete(synchronize_session=False)
            
            # 6. 删除对话记录
            self.db.query(Conversation).filter(Conversation.resume_id == resume_id).delete(synchronize_session=False)
            
            # 7. 删除匹配记录
            self.db.query(Match).filter(Match.resume_id == resume_id).delete(synchronize_session=False)
            
            # 8. 删除简历
            self.db.delete(resume)
            
            # 统一提交
            self.db.commit()
            
            # 删除文件
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            
            return True
        except Exception as e:
            self.db.rollback()
            print(f"删除简历失败: {e}")
            return False