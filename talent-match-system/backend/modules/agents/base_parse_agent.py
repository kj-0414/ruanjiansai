import json
import re
import logging
from typing import Dict, Any, List, Optional
from functools import lru_cache
from utils.qwen_client import get_qwen_client
from modules.knowledge_base.db import KnowledgeBaseDB
from modules.agents.reasoning.react import ReActAgent
from modules.agents.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS = {
    "编程语言": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin"],
    "框架": ["vue", "react", "angular", "django", "flask", "spring", "next", "nuxt", "express", "nest"],
    "数据库": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch", "sqlite", "oracle", "sql"],
    "工具": ["git", "docker", "kubernetes", "jenkins", "linux", "aws", "azure", "gcp", "nginx", "webpack"]
}

COMMON_SKILLS = [
    'python', 'java', 'javascript', 'typescript', 'vue', 'react', 'node', 'django',
    'flask', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes',
    'html', 'css', 'git', 'jenkins', 'linux', 'sql', 'webpack', 'go', 'rust'
]


class BaseParseAgent:
    """解析器基类，包含共同的解析逻辑"""

    def __init__(self):
        self.qwen_client = get_qwen_client()
        self.knowledge_base = KnowledgeBaseDB()
        self.tool_registry = self._initialize_tools()
        self.react_agent = ReActAgent(
            llm_client=get_qwen_client(),
            tool_executor=self.tool_registry
        )
        self.max_cache_size = 100

    def _initialize_tools(self) -> ToolRegistry:
        """初始化工具注册表"""
        raise NotImplementedError("Subclasses must implement _initialize_tools")

    def _normalize_skill(self, skill: str) -> str:
        """标准化技能名称"""
        return skill.lower().strip().replace(" ", "")

    def _normalize_skill_with_kb(self, skill: str, db=None) -> Optional[str]:
        """使用知识库标准化技能"""
        try:
            if db:
                kb_skill = self.knowledge_base.get_skill_by_name(skill, db=db)
            else:
                kb_skill = self.knowledge_base.get_skill_by_name(skill)

            if kb_skill:
                return kb_skill.get("skill_name", skill)

            skill_lower = skill.lower()
            if db:
                all_skills = self.knowledge_base.get_all_skills(db=db)
            else:
                all_skills = self.knowledge_base.get_all_skills()

            for kb_skill in all_skills:
                kb_name = kb_skill.get("skill_name", "").lower()
                aliases = [a.lower() for a in kb_skill.get("aliases", [])]

                if skill_lower == kb_name or skill_lower in aliases:
                    return kb_skill.get("skill_name", skill)
        except Exception as e:
            logger.warning(f"Skill normalization failed for {skill}: {e}")

        return skill

    def _parse_skills(self, skills: list, db=None) -> list:
        """解析技能列表"""
        result = []
        for skill in skills:
            if isinstance(skill, str):
                skill_name = skill.strip()
            elif isinstance(skill, dict) and "skill_name" in skill:
                skill_name = skill["skill_name"].strip()
            else:
                continue

            normalized = self._normalize_skill_with_kb(skill_name, db)
            if normalized and normalized not in result:
                result.append(normalized)

        return result

    def _categorize_skills(self, skills: List[str], db=None, filter_empty: bool = True) -> Dict[str, List[str]]:
        """对技能进行分类"""
        categories = {
            "编程语言": [],
            "框架": [],
            "数据库": [],
            "工具": [],
            "其他": []
        }

        for skill in skills:
            skill_lower = skill.lower()
            categorized = False

            for category, keywords in CATEGORY_KEYWORDS.items():
                if any(kw in skill_lower for kw in keywords):
                    categories[category].append(skill)
                    categorized = True
                    break

            if not categorized:
                categories["其他"].append(skill)

        if filter_empty:
            return {k: v for k, v in categories.items() if v}
        return categories

    def _get_trend_label(self, trend: float) -> str:
        """获取趋势标签"""
        if trend > 10:
            return "快速上升"
        elif trend > 0:
            return "上升"
        elif trend == 0:
            return "稳定"
        elif trend > -5:
            return "下降"
        else:
            return "快速下降"

    @lru_cache(maxsize=100)
    def _get_cached_result(self, cache_key: int) -> Optional[Dict]:
        """获取缓存结果（LRU缓存）"""
        return None

    def _add_to_cache(self, cache_key: int, result: dict):
        """添加到缓存（使用lru_cache装饰器）"""
        pass

    def _extract_skills_from_text(self, text: str, db=None) -> list:
        """从文本中提取技能"""
        skills = []
        text_lower = text.lower()

        for skill in COMMON_SKILLS:
            if skill in text_lower:
                normalized = self._normalize_skill_with_kb(skill.capitalize(), db)
                if normalized and normalized not in skills:
                    skills.append(normalized)

        return skills

    def _parse_json_with_fallback(self, text: str) -> Optional[Dict]:
        """解析JSON，带多种fallback策略"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass

        return None
