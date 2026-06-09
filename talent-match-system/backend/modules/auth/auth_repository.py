from sqlalchemy.orm import Session
from models import User as UserModel
from datetime import datetime
import json
import uuid


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_phone(self, phone: str) -> UserModel:
        return self.db.query(UserModel).filter(UserModel.phone == phone).first()

    def get_user_by_phone_and_role(self, phone: str, role: str) -> UserModel:
        return self.db.query(UserModel).filter(
            UserModel.phone == phone,
            UserModel.roles.like(f"%{role}%")
        ).first()

    def get_user_by_id(self, user_id: str) -> UserModel:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def create_user(self, phone: str, hashed_password: str, nickname: str, role: str = "job_seeker") -> UserModel:
        user_id = str(uuid.uuid4())
        new_user = UserModel(
            id=user_id,
            phone=phone,
            password=hashed_password,
            nickname=nickname,
            roles=json.dumps([role]),
            created_at=datetime.now()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def update_user(self, user_id: str, data: dict) -> UserModel:
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user