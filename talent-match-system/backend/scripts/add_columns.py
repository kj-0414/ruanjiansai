import sys
sys.path.insert(0, '.')
from models import engine, SessionLocal
from sqlalchemy import text

# 创建会话
db = SessionLocal()

try:
    # 为 resumes 表添加 internship_experience 字段
    print("正在为 resumes 表添加 internship_experience 字段...")
    db.execute(text('ALTER TABLE RESUMES ADD COLUMN internship_experience TEXT'))
    
    # 为 ai_resume_parse 表添加 internship_experience 字段
    print("正在为 ai_resume_parse 表添加 internship_experience 字段...")
    db.execute(text('ALTER TABLE AI_RESUME_PARSE ADD COLUMN internship_experience TEXT'))
    
    db.commit()
    print("字段添加成功！")
except Exception as e:
    print(f"字段可能已存在或添加失败: {e}")
    db.rollback()
finally:
    db.close()
