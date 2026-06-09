"""
技能相关工具
提供技能标准化、查询、推荐等功能
"""

import time
from typing import Dict, Any, Optional, List
from .base import BaseTool, ToolResult


class NormalizeSkillTool(BaseTool):
    """技能标准化工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="normalize_skill",
            description="标准化技能名称，支持别名识别。例如：python -> Python",
            parameters=[
                {"name": "skill_name", "type": "string", "description": "技能名称或别名", "required": True}
            ]
        )
        self.kb_service = kb_service

    def _get_kb_service(self):
        """延迟加载知识库服务"""
        if self.kb_service is None:
            try:
                from modules.knowledge_base import KnowledgeBaseService
                self.kb_service = KnowledgeBaseService()
            except Exception as e:
                self.logger.error(f"Failed to load knowledge base: {e}")
                return None
        return self.kb_service

    async def execute(self, skill_name: str) -> ToolResult:
        """执行技能标准化"""
        start_time = time.time()

        try:
            kb = self._get_kb_service()
            if kb is None:
                return ToolResult(
                    success=False,
                    error="知识库服务不可用"
                )

            result = kb.normalize_skill(skill_name)

            return ToolResult(
                success=True,
                data=result,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to normalize skill: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )


class GetRelatedSkillsTool(BaseTool):
    """获取相关技能工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="get_related_skills",
            description="获取与指定技能相关的其他技能列表",
            parameters=[
                {"name": "skill_id", "type": "integer", "description": "技能ID", "required": True},
                {"name": "limit", "type": "integer", "description": "返回数量限制", "required": False}
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

    async def execute(self, skill_id: int, limit: int = 10) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()
            if kb is None:
                return ToolResult(success=False, error="知识库服务不可用")

            related = kb.get_related_skills(skill_id, max_count=limit)

            return ToolResult(
                success=True,
                data=related,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to get related skills: {e}")
            return ToolResult(success=False, error=str(e))


class GetSkillRecommendationsTool(BaseTool):
    """获取技能推荐工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="get_skill_recommendations",
            description="基于已有技能推荐学习的新技能",
            parameters=[
                {"name": "skill_name", "type": "string", "description": "基础技能名称", "required": True},
                {"name": "limit", "type": "integer", "description": "推荐数量", "required": False}
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

    async def execute(self, skill_name: str, limit: int = 5) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()
            if kb is None:
                return ToolResult(success=False, error="知识库服务不可用")

            recommendations = kb.get_skill_recommendations(skill_name, limit=limit)

            return ToolResult(
                success=True,
                data=recommendations,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            return ToolResult(success=False, error=str(e))


class GetSkillTrendTool(BaseTool):
    """获取技能趋势工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="get_skill_trend",
            description="获取技能的市场需求趋势",
            parameters=[
                {"name": "skill_name", "type": "string", "description": "技能名称", "required": True},
                {"name": "start_period", "type": "string", "description": "开始时间 (YYYY-MM)", "required": False},
                {"name": "end_period", "type": "string", "description": "结束时间 (YYYY-MM)", "required": False}
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

    async def execute(self, skill_name: str, start_period: str = None, end_period: str = None) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()
            if kb is None:
                return ToolResult(success=False, error="知识库服务不可用")

            trend = kb.get_skill_trend(skill_name, start_period, end_period)

            return ToolResult(
                success=True,
                data=trend,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to get skill trend: {e}")
            return ToolResult(success=False, error=str(e))


normalize_skill_tool = NormalizeSkillTool()
get_related_skills_tool = GetRelatedSkillsTool()
get_skill_recommendations_tool = GetSkillRecommendationsTool()
get_skill_trend_tool = GetSkillTrendTool()
