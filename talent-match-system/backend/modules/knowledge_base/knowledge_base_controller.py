"""
知识库API控制器
提供RESTful API接口
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from .knowledge_base_agent import KnowledgeBaseAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge-base", tags=["知识库"])

kb_agent = KnowledgeBaseAgent()


class SkillQueryRequest(BaseModel):
    skill_name: str


class SkillsNormalizeRequest(BaseModel):
    skills: List[str]


class LearningPathRequest(BaseModel):
    from_skill: str
    to_skill: str


class RecommendSkillsRequest(BaseModel):
    base_skills: List[str]
    target_role: Optional[str] = None
    limit: int = 10


class EnhanceResumeSkillsRequest(BaseModel):
    skills: List[str]


class SkillTrendRequest(BaseModel):
    skill_names: List[str]


@router.post("/query")
async def query_skill(request: SkillQueryRequest) -> Dict[str, Any]:
    """查询技能信息"""
    try:
        result = kb_agent.query_skill(request.skill_name)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"查询技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/normalize")
async def normalize_skills(request: SkillsNormalizeRequest) -> Dict[str, Any]:
    """批量标准化技能名称"""
    try:
        results = kb_agent.normalize_skills(request.skills)
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"标准化技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning-path")
async def get_learning_path(request: LearningPathRequest) -> Dict[str, Any]:
    """获取技能学习路径"""
    try:
        path = kb_agent.get_learning_path(request.from_skill, request.to_skill)
        return {"success": True, "data": path}
    except Exception as e:
        logger.error(f"获取学习路径失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
async def recommend_skills(request: RecommendSkillsRequest) -> Dict[str, Any]:
    """推荐相关技能"""
    try:
        recommendations = kb_agent.recommend_skills(
            request.base_skills,
            request.target_role,
            request.limit
        )
        return {"success": True, "data": recommendations}
    except Exception as e:
        logger.error(f"推荐技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance-resume")
async def enhance_resume_skills(request: EnhanceResumeSkillsRequest) -> Dict[str, Any]:
    """增强简历技能"""
    try:
        result = kb_agent.enhance_resume_skills(request.skills)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"增强简历技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends")
async def get_skill_trends(request: SkillTrendRequest) -> Dict[str, Any]:
    """批量获取技能趋势"""
    try:
        result = kb_agent.get_skill_trends(request.skill_names)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"获取技能趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_skills(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量")
) -> Dict[str, Any]:
    """搜索技能"""
    try:
        results = kb_agent.search_skills_by_keyword(keyword, limit)
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"搜索技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-skills")
async def get_hot_skills(limit: int = Query(50, ge=1, le=100)) -> Dict[str, Any]:
    """获取热门技能"""
    try:
        skills = kb_agent.get_hot_skills(limit)
        return {"success": True, "data": skills}
    except Exception as e:
        logger.error(f"获取热门技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """获取知识库统计信息"""
    try:
        stats = kb_agent.get_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """健康检查"""
    return {"status": "healthy", "service": "knowledge-base"}
