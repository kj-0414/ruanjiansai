"""
解析相关工具
提供简历解析、岗位解析等功能
"""

import time
from typing import Dict, Any, List, Optional
from .base import BaseTool, ToolResult


class ParseResumeTool(BaseTool):
    """解析简历工具"""

    def __init__(self):
        super().__init__(
            name="parse_resume",
            description="使用AI解析简历文本，提取结构化信息",
            parameters=[
                {"name": "resume_text", "type": "string", "description": "简历文本内容", "required": True},
                {"name": "use_ai", "type": "boolean", "description": "是否使用AI解析", "required": False}
            ]
        )

    async def execute(self, resume_text: str, use_ai: bool = True) -> ToolResult:
        start_time = time.time()

        try:
            from modules.agents import ResumeParseAgent
            agent = ResumeParseAgent()

            if use_ai:
                result = await agent.parse_resume(resume_text)
            else:
                result = agent._extract_resume_info_fallback(resume_text)

            return ToolResult(
                success=True,
                data=result,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to parse resume: {e}")
            return ToolResult(success=False, error=str(e))


class ParseJobTool(BaseTool):
    """解析岗位工具"""

    def __init__(self):
        super().__init__(
            name="parse_job",
            description="使用AI解析岗位描述，提取结构化信息",
            parameters=[
                {"name": "job_text", "type": "string", "description": "岗位描述文本", "required": True},
                {"name": "use_ai", "type": "boolean", "description": "是否使用AI解析", "required": False}
            ]
        )

    async def execute(self, job_text: str, use_ai: bool = True) -> ToolResult:
        start_time = time.time()

        try:
            from modules.agents import JobParseAgent
            agent = JobParseAgent()

            if use_ai:
                result = await agent.parse_job(job_text)
            else:
                result = agent._extract_job_info_fallback(job_text)

            return ToolResult(
                success=True,
                data=result,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to parse job: {e}")
            return ToolResult(success=False, error=str(e))


class ExtractSkillsTool(BaseTool):
    """提取技能工具"""

    def __init__(self, kb_service=None):
        super().__init__(
            name="extract_skills",
            description="从文本中提取技能并标准化",
            parameters=[
                {"name": "text", "type": "string", "description": "输入文本", "required": True},
                {"name": "normalize", "type": "boolean", "description": "是否标准化技能名称", "required": False}
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

    async def execute(self, text: str, normalize: bool = True) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()
            if kb is None:
                return ToolResult(success=False, error="知识库服务不可用")

            text_lower = text.lower()
            all_skills = kb.db.get_all_skills()

            found_skills = []
            for skill in all_skills:
                skill_name = skill.get('skill_name', '').lower()
                if skill_name in text_lower:
                    found_skills.append(skill)

                aliases_text = skill.get('skill_aliases', '[]')
                try:
                    import json
                    aliases = json.loads(aliases_text)
                    for alias in aliases:
                        if alias.lower() in text_lower:
                            found_skills.append(skill)
                            break
                except:
                    pass

            if normalize:
                normalized = {}
                for skill in found_skills:
                    skill_name = skill.get('skill_name')
                    if skill_name not in normalized:
                        normalized[skill_name] = skill

                found_skills = list(normalized.values())

            return ToolResult(
                success=True,
                data={
                    "skills": [
                        {
                            "name": s.get('skill_name'),
                            "category": s.get('category'),
                            "skill_id": s.get('skill_id')
                        }
                        for s in found_skills
                    ],
                    "count": len(found_skills)
                },
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Failed to extract skills: {e}")
            return ToolResult(success=False, error=str(e))


parse_resume_tool = ParseResumeTool()
parse_job_tool = ParseJobTool()
extract_skills_tool = ExtractSkillsTool()
