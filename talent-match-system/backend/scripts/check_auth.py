from core.database import SessionLocal, User
from jose import jwt
from core.config import settings

db = SessionLocal()

# 获取所有用户
users = db.query(User).all()
print(f"数据库中共有 {len(users)} 个用户:")
for user in users:
    print(f"  - ID: {user.id}, Phone: {user.phone}, Roles: {user.roles}")

# 测试 JWT token 生成和验证
if users:
    user = users[0]
    print(f"\n测试 JWT token (用户: {user.phone}):")
    print(f"  用户ID: {user.id}")

    # 生成 token
    from datetime import timedelta
    access_token = jwt.encode(
        {"sub": user.id},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    print(f"  生成的Token: {access_token[:50]}...")

    # 验证 token
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"  Token验证成功，payload: {payload}")
    except Exception as e:
        print(f"  Token验证失败: {e}")

db.close()
