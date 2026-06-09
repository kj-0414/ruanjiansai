from fastapi import APIRouter, Depends, HTTPException, status
from modules.storage.storage_service import StorageService
from sqlalchemy.orm import Session
from models import get_db

router = APIRouter()
storage_service = StorageService()

# 模块接口
@router.get("/")
async def get_storage(db: Session = Depends(get_db)):
    return {"message": "Storage module"}