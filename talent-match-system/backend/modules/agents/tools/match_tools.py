"""
匹配相关工具
提供人岗匹配、分数计算等功能
"""

import time
from typing import Dict, Any, List
from .base import BaseTool, ToolResult


class CalculateMatchTool(BaseTool):
    """计算匹配分数工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="calculate_match",
            description="计算简历与岗位的匹配分数",
            parameters=[
                {"name": "resume_skills", "type": "array", "description": "简历技能列表", "required": True},
                {"name": "job_skills", "type": "array", "description": "岗位技能列表", "required": True},
                {"name": "resume_experience", "type": "integer", "description": "简历工作年限", "required": False},
                {"name": "job_experience", "type": "integer", "description": "岗位要求工作年限", "required": False}
            ]
        )
        self.kb_service = kb_service

    def _get_kb_service(self):
        if self.kb_service is None:
            try:
                from modules.knowledge_base import KnowledgeBaseService
                self.kb_service = KnowledgeBaseService()
            except:
                return None
        return self.kb_service

    async def execute(
        self,
        resume_skills: List[str],
        job_skills: List[str],
        resume_experience: int = None,
        job_experience: int = None
    ) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()

            if kb is None:
                return ToolResult(success=False, error="知识库服务不可用")

            result = kb.enhance_match(resume_skills, job_skills)

            experience_score = 100
            if resume_experience and job_experience:
                exp_diff = abs(resume_experience - job_experience)
                experience_score = max(0, 100 - exp_diff * 20)

            return ToolResult(
                success=True,
                data={
                    "skill_match": result,
                    "experience_score": experience_score,
                    "overall_score": (
                        result.get('enhanced_score', 0) * 0.7 +
                        experience_score * 0.3
                    )
                },
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to calculate match: {e}")
            return ToolResult(success=False, error=str(e))


class EnhanceMatchTool(BaseTool):
    """增强匹配工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="enhance_match",
            description="使用知识库增强简历与岗位的匹配分析",
            parameters=[
                {"name": "resume_skills", "type": "array", "description": "简历技能列表", "required": True},
                {"name": "job_skills", "type": "array", "description": "岗位技能列表", "required": True}
            ]
        )
        self.kb_service = kb_service

    def _get_kb_service(self):
        if self.kb_service is None:
            try:
                from modules.knowledge_base import KnowledgeBaseService
                self.kb_service = KnowledgeBaseService()
            except:
                return None
        return self.kb_service

    async def execute(self, resume_skills: List[str], job_skills: List[str]) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()
            if kb is None:
                return ToolResult(success=False, error="知识库服务不可用")

            result = kb.enhance_match(resume_skills, job_skills)

            return ToolResult(
                success=True,
                data=result,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to enhance match: {e}")
            return ToolResult(success=False, error=str(e))


class GetSkillGapTool(BaseTool):
    """获取技能差距工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="get_skill_gap",
            description="分析简历技能与岗位要求之间的差距",
            parameters=[
                {"name": "resume_skills", "type": "array", "description": "简历技能列表", "required": True},
                {"name": "job_skills", "type": "array", "description": "岗位技能列表", "required": True},
                {"name": "include_recommendations", "type": "boolean", "description": "是否包含推荐", "required": False}
            ]
        )
        self.kb_service = kb_service

    def _get_kb_service(self):
        if self.kb_service is None:
            try:
                from modules.knowledge_base import KnowledgeBaseService
                self.kb_service = KnowledgeBaseService()
            except:
                return None
        return self.kb_service

    async def execute(
        self,
        resume_skills: List[str],
        job_skills: List[str],
        include_recommendations: bool = True
    ) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()
            if kb is None:
                return ToolResult(success=False, error="知识库服务不可用")

            result = kb.enhance_match(resume_skills, job_skills)

            missing_skills = result.get('missing_skills', [])

            gap_analysis = {
                "missing_skills": missing_skills,
                "missing_count": len(missing_skills),
                "match_rate": result.get('direct_score', 0)
            }

            if include_recommendations and missing_skills:
                recommendations = {}
                for skill in missing_skills[:5]:
                    recs = kb.get_skill_recommendations(skill, limit=3)
                    recommendations[skill] = [
                        {"skill": r.get('skill_name'), "reason": r.get('suggestion')}
                        for r in recs
                    ]
                gap_analysis["recommendations"] = recommendations

            return ToolResult(
                success=True,
                data=gap_analysis,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to get skill gap: {e}")
            return ToolResult(success=False, error=str(e))


calculate_match_tool = CalculateMatchTool()
enhance_match_tool = EnhanceMatchTool()
get_skill_gap_tool = GetSkillGapTool()
