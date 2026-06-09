import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from models import User, engine, SessionLocal

def create_admin_account(phone: str, password: str):
    session = SessionLocal()
    
    try:
        existing_user = session.query(User).filter(User.phone == phone).first()
        if existing_user:
            print(f"用户 {phone} 已存在，正在更新角色...")
            existing_user.roles = '["job_seeker", "company", "admin"]'
            session.commit()
            print(f"用户 {phone} 已升级为管理员")
            return
        
        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)
        
        new_admin = User(
            id=user_id,
            phone=phone,
            password=hashed_password,
            roles='["job_seeker", "company", "admin"]',
            created_at=datetime.now()
        )
        
        session.add(new_admin)
        session.commit()
        session.refresh(new_admin)
        
        print(f"管理员账号创建成功！")
        print(f"手机号: {phone}")
        print(f"密码: {password}")
        print(f"用户ID: {user_id}")
        
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="创建管理员账号")
    parser.add_argument("--phone", required=True, help="管理员手机号")
    parser.add_argument("--password", required=True, help="管理员密码")
    
    args = parser.parse_args()
    
    create_admin_account(args.phone, args.password)