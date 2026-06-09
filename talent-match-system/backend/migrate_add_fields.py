"""
数据库迁移脚本：添加年龄和毕业时间字段
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import engine
from sqlalchemy import text

def migrate_add_fields():
    """添加 candidate_age 和 grad_date 字段到 resumes 表"""
    with engine.connect() as conn:
        # 检查 candidate_age 字段是否存在
        result = conn.execute(text("""
            SELECT COUNT(*) FROM USER_TAB_COLUMNS
            WHERE TABLE_NAME = 'RESUMES' AND COLUMN_NAME = 'CANDIDATE_AGE'
        """))
        if result.scalar() == 0:
            print("添加 CANDIDATE_AGE 字段...")
            conn.execute(text("ALTER TABLE resumes ADD candidate_age INTEGER"))
            conn.commit()
            print("CANDIDATE_AGE 字段添加成功")
        else:
            print("CANDIDATE_AGE 字段已存在")

        # 检查 grad_date 字段是否存在
        result = conn.execute(text("""
            SELECT COUNT(*) FROM USER_TAB_COLUMNS
            WHERE TABLE_NAME = 'RESUMES' AND COLUMN_NAME = 'GRAD_DATE'
        """))
        if result.scalar() == 0:
            print("添加 GRAD_DATE 字段...")
            conn.execute(text("ALTER TABLE resumes ADD grad_date VARCHAR(20)"))
            conn.commit()
            print("GRAD_DATE 字段添加成功")
        else:
            print("GRAD_DATE 字段已存在")

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate_add_fields()
    print("迁移完成！")
