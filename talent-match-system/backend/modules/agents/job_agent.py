import re
import logging
from typing import Dict, Any, List, Optional
from functools import lru_cache
from utils.prompt_templates import get_job_prompt
from modules.agents.base_parse_agent import BaseParseAgent
from modules.agents.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class JobParseAgent(BaseParseAgent):
    """岗位需求解析智能体"""

    def __init__(self):
        super().__init__()
        self._parse_cache = {}
        self.jd_splitter = None

    def _get_jd_splitter(self):
        """延迟加载JD切分器"""
        if self.jd_splitter is None:
            from utils.text_splitter import JDSplitter
            self.jd_splitter = JDSplitter()
        return self.jd_splitter

    def _initialize_tools(self) -> ToolRegistry:
        """初始化工具注册表"""
        registry = ToolRegistry()
        from .tools.parse_tools import parse_job_tool, extract_skills_tool
        from .tools.skill_tools import normalize_skill_tool
        registry.register(parse_job_tool)
        registry.register(extract_skills_tool)
        registry.register(normalize_skill_tool)
        return registry

    @lru_cache(maxsize=100)
    def parse_job(self, job_text: str, use_reasoning: bool = False, db=None) -> dict:
        """解析岗位需求（支持语义切分）"""
        if not job_text or job_text.strip() == "":
            return self._get_empty_profile()

        try:
            if len(job_text) > 2000:
                return self._parse_with_semantic_split(job_text, db)
            elif use_reasoning:
                return self._parse_with_reasoning(job_text, db)
            else:
                return self._parse_standard(job_text, db)
        except Exception as e:
            logger.error(f"Job parse failed: {e}", exc_info=True)
            return self._parse_job_fallback(job_text, db)

    def _parse_with_semantic_split(self, job_text: str, db=None) -> dict:
        """使用语义切分解析JD"""
        splitter = self._get_jd_splitter()
        chunks = splitter.split_jd(job_text)

        if not chunks:
            return self._parse_standard(job_text, db)

        result = {
            "job_title": "未提供",
            "salary_range": "未提供",
            "location": "未提供",
            "job_type": "全职",
            "required_skills": [],
            "required_education": "未提供",
            "required_experience": "未提供",
            "job_responsibilities": [],
            "job_requirements": [],
            "benefits": [],
            "company_intro": "",
            "highlights": [],
            "source": "semantic_split",
            "confidence": 0.75
        }

        skills_set = set()

        for chunk in chunks:
            chunk_type = chunk['type']
            content = chunk['content']

            try:
                prompt = get_job_prompt(content)
                response = self.qwen_client.chat(prompt)
                if response.get("success"):
                    parsed = self.qwen_client.parse_json_response(response["content"])
                    if parsed:
                        if chunk_type == 'responsibility':
                            result["job_responsibilities"].extend(parsed.get("job_responsibilities", []))
                        elif chunk_type == 'hard_requirement':
                            result["required_education"] = parsed.get("required_education", result["required_education"])
                            result["required_experience"] = parsed.get("required_experience", result["required_experience"])
                        elif chunk_type == 'soft_requirement':
                            for skill in parsed.get("required_skills", []):
                                if isinstance(skill, str):
                                    normalized = self._normalize_skill_with_kb(skill.strip(), db)
                                    if normalized:
                                        skills_set.add(normalized)

                        if parsed.get("job_title") and result["job_title"] == "未提供":
                            result["job_title"] = parsed["job_title"]
                        if parsed.get("salary_range") and result["salary_range"] == "未提供":
                            result["salary_range"] = parsed["salary_range"]
                        if parsed.get("location") and result["location"] == "未提供":
                            result["location"] = parsed["location"]
            except Exception as e:
                logger.warning(f"JD chunk parse failed for {chunk_type}: {e}")

        result["required_skills"] = list(skills_set)
        result["skill_categories"] = self._categorize_skills(list(skills_set), db)
        result["skill_difficulty_level"] = self._estimate_skill_difficulty(list(skills_set), db)

        skill_details = self._analyze_required_skills(list(skills_set), db)
        result["hot_required_skills"] = skill_details["hot_required_skills"]
        result["rare_required_skills"] = skill_details["rare_required_skills"]
        result["skill_demand"] = skill_details["skill_demand"]
        result["skill_trends"] = skill_details["skill_trends"]

        return result

    def _parse_standard(self, job_text: str, db=None) -> dict:
        """标准解析方法"""
        try:
            prompt = get_job_prompt(job_text)
            response = self.qwen_client.chat(prompt)

            if response.get("success"):
                parsed_result = self.qwen_client.parse_json_response(response["content"])
                if parsed_result:
                    normalized = self._normalize_profile(parsed_result, db)
                    return normalized
        except Exception as e:
            logger.warning(f"AI job parse failed, falling back: {e}")

        return self._parse_job_fallback(job_text, db)

    async def _parse_with_reasoning(self, job_text: str, db=None) -> dict:
        """使用推理模式解析"""
        reasoning_context = f"""
        Job posting to parse:
        {job_text[:1000]}

        Please analyze and extract:
        1. Job title and basic info
        2. Required skills and qualifications
        3. Experience requirements
        4. Education requirements
        5. Salary range and benefits
        """

        try:
            result = await self.react_agent.think(
                question=reasoning_context,
                context=str(db) if db else ""
            )

            if result and result.get("answer"):
                parsed = self._parse_reasoning_result(result["answer"])
                if parsed:
                    normalized = self._normalize_profile(parsed, db)
                    return normalized
        except Exception as e:
            logger.warning(f"Reasoning parse failed, falling back: {e}")

        return self._parse_standard(job_text, db)

    def _parse_reasoning_result(self, answer: str) -> Optional[Dict]:
        """解析推理结果"""
        try:
            if answer.strip().startswith("{"):
                return self._parse_json_with_fallback(answer)

            patterns = [
                r'"job_title":\s*"([^"]+)"',
                r'"required_skills":\s*\[([^\]]+)\]',
                r'"required_education":\s*"([^"]+)"',
                r'"required_experience":\s*"([^"]+)"',
                r'"salary_range":\s*"([^"]+)"',
            ]

            result = {}
            for pattern in patterns:
                match = re.search(pattern, answer)
                if match:
                    key = pattern.split('"')[1]
                    value = match.group(1)
                    if key == "required_skills":
                        result[key] = [s.strip().strip('"') for s in value.split(",")]
                    else:
                        result[key] = value

            return result if result else None
        except Exception as e:
            logger.warning(f"Failed to parse reasoning result: {e}")
            return None

    def _normalize_profile(self, parsed_result: dict, db=None) -> dict:
        """标准化岗位档案"""
        skills = self._parse_skills(parsed_result.get("required_skills", []), db)
        skill_details = self._analyze_required_skills(skills, db)

        return {
            "job_title": parsed_result.get("job_title", "未提供"),
            "salary_range": parsed_result.get("salary_range", "未提供"),
            "location": parsed_result.get("location", "未提供"),
            "job_type": parsed_result.get("job_type", "全职"),
            "required_skills": skills,
            "required_education": parsed_result.get("required_education", "未提供"),
            "required_experience": parsed_result.get("required_experience", "未提供"),
            "job_responsibilities": parsed_result.get("job_responsibilities", []),
            "job_requirements": parsed_result.get("job_requirements", []),
            "benefits": parsed_result.get("benefits", []),
            "company_intro": parsed_result.get("company_intro", ""),
            "highlights": parsed_result.get("highlights", []),
            "source": parsed_result.get("source", "ai"),
            "confidence": parsed_result.get("confidence", 0.8),
            "skill_categories": self._categorize_skills(skills, db),
            "skill_difficulty_level": self._estimate_skill_difficulty(skills, db),
            "hot_required_skills": skill_details["hot_required_skills"],
            "rare_required_skills": skill_details["rare_required_skills"],
            "skill_demand": skill_details["skill_demand"],
            "skill_trends": skill_details["skill_trends"]
        }

    def _estimate_skill_difficulty(self, skills: List[str], db=None) -> str:
        """估计技能难度级别"""
        if not skills:
            return "unknown"

        easy_count = 0
        hard_count = 0

        for skill in skills:
            try:
                if db:
                    kb_skill = self.knowledge_base.get_skill_by_name(skill, db=db)
                else:
                    kb_skill = self.knowledge_base.get_skill_by_name(skill)

                if kb_skill:
                    difficulty = kb_skill.get("difficulty", "medium")
                    if difficulty == "easy":
                        easy_count += 1
                    elif difficulty == "hard":
                        hard_count += 1
            except Exception as e:
                logger.warning(f"Failed to get skill difficulty for {skill}: {e}")

        total = len(skills)
        if hard_count > total * 0.5:
            return "高级"
        elif easy_count > total * 0.5:
            return "入门"
        else:
            return "中级"

    def _analyze_required_skills(self, skills: List[str], db=None) -> Dict:
        """分析岗位要求技能的市场数据"""
        hot_skills = []
        rare_skills = []
        skill_demand = {}
        skill_trends = {}

        try:
            for skill in skills:
                if db:
                    skill_info = self.knowledge_base.get_skill_info(skill, db=db)
                else:
                    skill_info = self.knowledge_base.get_skill_info(skill)

                if skill_info:
                    demand_weight = skill_info.get("demand_weight", 0)
                    avg_demand = skill_info.get("avg_demand", 0)
                    trend = skill_info.get("demand_trend", 0)
                    cooccurrence_count = skill_info.get("cooccurrence_count", 0)

                    skill_demand[skill] = {
                        "weight": demand_weight,
                        "avg_demand": avg_demand
                    }

                    skill_trends[skill] = {
                        "trend": trend,
                        "trend_label": self._get_trend_label(trend)
                    }

                    if demand_weight > 0.002:
                        hot_skills.append({
                            "skill": skill,
                            "demand_weight": demand_weight,
                            "avg_demand": avg_demand
                        })

                    if demand_weight > 0.0015 and cooccurrence_count < 100:
                        rare_skills.append({
                            "skill": skill,
                            "demand_weight": demand_weight,
                            "cooccurrence_count": cooccurrence_count
                        })

            hot_skills.sort(key=lambda x: x["demand_weight"], reverse=True)
            rare_skills.sort(key=lambda x: x["demand_weight"], reverse=True)

        except Exception as e:
            logger.error(f"Skill analysis failed: {e}", exc_info=True)

        return {
            "hot_required_skills": hot_skills[:3],
            "rare_required_skills": rare_skills[:2],
            "skill_demand": skill_demand,
            "skill_trends": skill_trends
        }

    def _parse_job_fallback(self, job_text: str, db=None) -> dict:
        """降级解析方法"""
        skills = self._extract_skills_from_text(job_text, db)
        experience = self._extract_experience(job_text)
        education = self._extract_education(job_text)
        salary = self._extract_salary(job_text)
        location = self._extract_location(job_text)

        return {
            "job_title": self._extract_job_title(job_text),
            "salary_range": salary,
            "location": location,
            "job_type": "全职",
            "required_skills": skills,
            "required_education": education,
            "required_experience": experience,
            "job_responsibilities": [],
            "job_requirements": [],
            "benefits": [],
            "company_intro": "",
            "highlights": [],
            "source": "fallback",
            "confidence": 0.5,
            "skill_categories": self._categorize_skills(skills, db),
            "skill_difficulty_level": self._estimate_skill_difficulty(skills, db)
        }

    def _extract_job_title(self, text: str) -> str:
        """提取岗位名称"""
        patterns = [r'岗位名称[\s：:]([\u4e00-\u9fa5a-zA-Z]+)', r'职位[\s：:]([\u4e00-\u9fa5a-zA-Z]+)']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "未提供"

    def _extract_experience(self, text: str) -> str:
        """提取经验要求"""
        match = re.search(r'(\d+)\s*年[\s\S]*经验', text)
        if match:
            return f"{match.group(1)}年以上"
        return "未提供"

    def _extract_education(self, text: str) -> str:
        """提取学历要求"""
        edu_keywords = {
            '博士': ['博士'],
            '硕士': ['硕士', '研究生'],
            '本科': ['本科'],
            '大专': ['大专', '专科']
        }
        for level, keywords in edu_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return level + "及以上"
        return "未提供"

    def _extract_salary(self, text: str) -> str:
        """提取薪资范围"""
        match = re.search(r'(\d+)[Kk]-(\d+)[Kk]', text)
        if match:
            return f"{match.group(1)}K-{match.group(2)}K"
        match = re.search(r'(\d+)[Kk]以上', text)
        if match:
            return f"{match.group(1)}K以上"
        return "面议"

    def _extract_location(self, text: str) -> str:
        """提取工作地点"""
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '苏州']
        for city in cities:
            if city in text:
                return city
        return "未提供"

    def _get_empty_profile(self) -> dict:
        """获取空档案"""
        return {
            "job_title": "未提供",
            "salary_range": "未提供",
            "location": "未提供",
            "job_type": "全职",
            "required_skills": [],
            "required_education": "未提供",
            "required_experience": "未提供",
            "job_responsibilities": [],
            "job_requirements": [],
            "benefits": [],
            "company_intro": "",
            "highlights": [],
            "source": "empty",
            "confidence": 0,
            "skill_categories": {},
            "skill_difficulty_level": "unknown"
        }

    def validate_profile(self, profile: dict) -> dict:
        """验证档案"""
        errors = []

        if not profile.get("job_title") or profile["job_title"] == "未提供":
            errors.append("缺少岗位名称")

        if len(profile.get("required_skills", [])) == 0:
            errors.append("缺少技能要求")

        suggestions = []
        if len(profile.get("required_skills", [])) < 3:
            suggestions.append("建议补充更多技能要求以提高匹配准确性")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "suggestions": suggestions,
            "confidence": profile.get("confidence", 0)
        }

    def align_tags_with_resume(self, job_profile: dict, resume_profile: dict, db=None) -> dict:
        """将岗位标签与简历对齐"""
        job_skills = set(job_profile.get("required_skills", []))
        resume_skills = set(resume_profile.get("skills", []))

        aligned_skills = []
        for job_skill in job_skills:
            aligned = {
                "job_skill": job_skill,
                "resume_skill": None,
                "matched": False,
                "match_type": None,
                "normalized_job_skill": None,
                "normalized_resume_skill": None
            }

            job_normalized = self._normalize_skill_with_kb(job_skill, db)
            aligned["normalized_job_skill"] = job_normalized

            for resume_skill in resume_skills:
                resume_normalized = self._normalize_skill_with_kb(resume_skill, db)

                if job_normalized == resume_normalized:
                    aligned["resume_skill"] = resume_skill
                    aligned["normalized_resume_skill"] = resume_normalized
                    aligned["matched"] = True
                    aligned["match_type"] = "exact"
                    break
                elif self._check_semantic_match(job_skill, resume_skill):
                    aligned["resume_skill"] = resume_skill
                    aligned["normalized_resume_skill"] = resume_normalized
                    aligned["matched"] = True
                    aligned["match_type"] = "semantic"
                    break

            aligned_skills.append(aligned)

        return {
            "aligned_skills": aligned_skills,
            "total_required": len(job_skills),
            "matched_count": sum(1 for s in aligned_skills if s["matched"]),
            "match_summary": {
                "exact_match": sum(1 for s in aligned_skills if s.get("match_type") == "exact"),
                "semantic_match": sum(1 for s in aligned_skills if s.get("match_type") == "semantic"),
                "no_match": sum(1 for s in aligned_skills if not s["matched"])
            }
        }

    def _check_semantic_match(self, skill1: str, skill2: str) -> bool:
        """检查语义匹配"""
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()

        if skill1_lower in skill2_lower or skill2_lower in skill1_lower:
            return True

        semantic_pairs = {
            ("js", "javascript"),
            ("ts", "typescript"),
            ("py", "python"),
            ("vue.js", "vue"),
            ("react.js", "react"),
            ("node.js", "node"),
            ("k8s", "kubernetes")
        }

        for pair in semantic_pairs:
            if (skill1_lower in pair and skill2_lower in pair):
                return True

        return False

    def enrich_job_profile(self, profile: dict, db=None) -> dict:
        """丰富岗位档案信息"""
        enriched = profile.copy()

        enriched_skills = []
        for skill in profile.get("required_skills", []):
            enriched_skill = {
                "skill": skill,
                "category": "unknown",
                "difficulty": "medium",
                "related_skills": [],
                "market_demand": "unknown"
            }

            try:
                if db:
                    kb_skill = self.knowledge_base.get_skill_by_name(skill, db=db)
                else:
                    kb_skill = self.knowledge_base.get_skill_by_name(skill)

                if kb_skill:
                    enriched_skill["category"] = kb_skill.get("category", "unknown")
                    enriched_skill["difficulty"] = kb_skill.get("difficulty", "medium")
                    enriched_skill["description"] = kb_skill.get("description", "")

                    if db:
                        relations = self.knowledge_base.get_skill_relations(skill_name=skill, db=db)
                    else:
                        relations = self.knowledge_base.get_skill_relations(skill_name=skill)

                    enriched_skill["related_skills"] = [
                        r["target_skill"] for r in relations
                        if r.get("relation_type") in ["related_to", "belongs_to"]
                    ][:5]

                    enriched_skill["prerequisites"] = [
                        r["target_skill"] for r in relations
                        if r.get("relation_type") == "requires"
                    ]
            except Exception as e:
                logger.warning(f"Failed to enrich skill {skill}: {e}")

            enriched_skills.append(enriched_skill)

        enriched["skills_detail"] = enriched_skills
        enriched["skill_summary"] = {
            "total": len(enriched_skills),
            "by_category": self._summarize_by_category(enriched_skills),
            "difficulty_distribution": self._summarize_difficulty(enriched_skills)
        }

        return enriched

    def _summarize_by_category(self, skills_detail: List[dict]) -> dict:
        """按类别汇总技能"""
        summary = {}
        for skill_info in skills_detail:
            category = skill_info.get("category", "unknown")
            if category not in summary:
                summary[category] = []
            summary[category].append(skill_info["skill"])
        return summary

    def _summarize_difficulty(self, skills_detail: List[dict]) -> dict:
        """按难度分布汇总"""
        distribution = {"easy": [], "medium": [], "hard": [], "unknown": []}
        for skill_info in skills_detail:
            difficulty = skill_info.get("difficulty", "unknown")
            if difficulty in distribution:
                distribution[difficulty].append(skill_info["skill"])
        return {k: len(v) for k, v in distribution.items()}
