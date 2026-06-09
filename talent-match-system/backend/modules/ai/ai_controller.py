from fastapi import APIRouter, Depends, HTTPException, status
from modules.ai.ai_service import AIService
from sqlalchemy.orm import Session
from models import get_db
from pydantic import BaseModel
from typing import Union, Optional

router = APIRouter()
ai_service = AIService()

class AbilityCreateRequest(BaseModel):
    user_id: Union[str, int]
    ability_data: Optional[dict] = None

# 模块接口
@router.get("/")
async def get_ai(db: Session = Depends(get_db)):
    return {"message": "AI module"}

# 能力树相关接口
@router.get("/tree/{user_id}")
async def get_ability_tree(user_id: str, resume_id: str = None, db: Session = Depends(get_db)):
    try:
        result = ai_service.get_ability_tree(user_id, db, resume_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取能力树失败: {str(e)}"
        )

# 能力雷达图相关接口
@router.get("/radar/{user_id}")
async def get_ability_radar(user_id: str, resume_id: str = None, db: Session = Depends(get_db)):
    try:
        result = ai_service.get_ability_radar(user_id, db, resume_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取雷达图数据失败: {str(e)}"
        )

# 能力图谱创建接口
@router.post("/create")
async def create_ability_map(request: AbilityCreateRequest, db: Session = Depends(get_db)):
    try:
        result = ai_service.create_ability_map(request.user_id, request.ability_data, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建能力图谱失败: {str(e)}"
        )

# 文本分析接口
@router.get("/text/{user_id}")
async def get_text_analysis(user_id: str, resume_id: str = None, db: Session = Depends(get_db)):
    try:
        result = ai_service.get_text_analysis(user_id, db, resume_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文本分析失败: {str(e)}"
        )

# 能力宇宙接口
@router.get("/universe/{user_id}")
async def get_ability_universe(user_id: str, resume_id: str = None, db: Session = Depends(get_db)):
    """
    获取能力宇宙分析结果
    包含：能力宇宙总览、能力证据链、成长路径、贡献分析、文本报告
    """
    try:
        result = ai_service.get_ability_universe(user_id, db, resume_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取能力宇宙失败: {str(e)}"
        )