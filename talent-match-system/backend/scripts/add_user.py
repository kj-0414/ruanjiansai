from core.database import SessionLocal, User
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash

db = SessionLocal()

# 创建默认用户，使用正确的密码哈希
user = User(
    id=str(uuid.uuid4()),
    phone='13800138000',
    password=generate_password_hash('123456'),  # 密码是123456
    roles='["job_seeker", "company"]',
    created_at=datetime.now()
)

db.add(user)
db.commit()
print('默认用户已创建')
print(f'用户ID: {user.id}')
print('密码: 123456')