import re
import logging
from typing import Dict, Any, List, Optional
from functools import lru_cache
from utils.prompt_templates import get_resume_prompt
from modules.agents.base_parse_agent import BaseParseAgent
from modules.agents.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ResumeParseAgent(BaseParseAgent):
    """简历解析智能体"""

    def __init__(self):
        super().__init__()
        self._parse_cache = {}
        self.text_splitter = None

    def _get_text_splitter(self):
        """延迟加载文本切分器"""
        if self.text_splitter is None:
            from utils.text_splitter import ResumeSplitter
            self.text_splitter = ResumeSplitter()
        return self.text_splitter

    def parse_resume_from_file(self, file_path: str, db=None) -> dict:
        """从文件解析简历（支持PDF/DOCX/TXT）"""
        text = self._extract_text_from_file(file_path)
        return self.parse_resume(text, db=db)

    def _extract_text_from_file(self, file_path: str) -> str:
        """提取文件文本"""
        if file_path.endswith(".pdf"):
            try:
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                text = "\n".join([doc.page_content for doc in documents])
            except ImportError:
                text = self._fallback_file_read(file_path)
        elif file_path.endswith(".docx"):
            try:
                from langchain_community.document_loaders import Docx2txtLoader
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
                text = "\n".join([doc.page_content for doc in documents])
            except ImportError:
                text = self._fallback_file_read(file_path)
        else:
            text = self._fallback_file_read(file_path)

        return self._clean_ocr_text(text)

    def _fallback_file_read(self, file_path: str) -> str:
        """降级文件读取"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return ""

    def _clean_ocr_text(self, text: str) -> str:
        """OCR文本清洗：去除乱码和多余字符"""
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、；：（）《》【】·\-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _initialize_tools(self) -> ToolRegistry:
        """初始化工具注册表"""
        registry = ToolRegistry()
        from .tools.parse_tools import parse_resume_tool, extract_skills_tool
        from .tools.skill_tools import normalize_skill_tool
        from .tools.smart_resume_tool import smart_resume_parse_tool
        from .tools.skill_extraction_tool import skill_extraction_tool
        
        registry.register(parse_resume_tool)
        registry.register(extract_skills_tool)
        registry.register(normalize_skill_tool)
        registry.register(smart_resume_parse_tool)
        registry.register(skill_extraction_tool)
        return registry

    @lru_cache(maxsize=100)
    def parse_resume(self, resume_text: str, use_reasoning: bool = False, db=None) -> dict:
        """解析简历（支持结构化切分）"""
        if not resume_text or resume_text.strip() == "":
            return self._get_empty_profile()

        try:
            if len(resume_text) > 3000:
                return self._parse_with_chunking(resume_text, db)
            elif use_reasoning:
                return self._parse_with_reasoning(resume_text, db)
            else:
                return self._parse_standard(resume_text, db)
        except Exception as e:
            logger.error(f"Resume parse failed: {e}", exc_info=True)
            return self._parse_resume_fallback(resume_text, db)

    def _parse_with_chunking(self, resume_text: str, db=None) -> dict:
        """使用结构化切分解析长简历"""
        splitter = self._get_text_splitter()
        chunks = splitter.split_resume(resume_text)

        if not chunks:
            return self._parse_standard(resume_text, db)

        results = []
        skill_phrases = []

        for chunk in chunks:
            chunk_type = chunk['type']
            content = chunk['content']

            if chunk_type == 'skill_phrase':
                skill_phrases.append(content)
            else:
                try:
                    prompt = get_resume_prompt(content)
                    response = self.qwen_client.chat(prompt)
                    if response.get("success"):
                        parsed = self.qwen_client.parse_json_response(response["content"])
                        if parsed:
                            results.append(parsed)
                except Exception as e:
                    logger.warning(f"Chunk parse failed for {chunk_type}: {e}")

        return self._merge_chunk_results(results, skill_phrases, db)

    def _merge_chunk_results(self, results: List[dict], skill_phrases: List[str], db=None) -> dict:
        """合并多个chunk的解析结果"""
        merged = {
            "name": "未提供",
            "phone": "未提供",
            "email": "未提供",
            "education": "未提供",
            "experience_years": "未提供",
            "skills": [],
            "work_experience": [],
            "internship_experience": [],
            "education_history": [],
            "self_evaluation": "",
            "highlights": [],
            "source": "chunked",
            "confidence": 0.7
        }

        skills_set = set()

        for result in results:
            if result.get("name") and result["name"] != "未提供":
                merged["name"] = result["name"]
            if result.get("phone") and result["phone"] != "未提供":
                merged["phone"] = result["phone"]
            if result.get("email") and result["email"] != "未提供":
                merged["email"] = result["email"]
            if result.get("education") and result["education"] != "未提供":
                merged["education"] = result["education"]
            if result.get("experience_years") and result["experience_years"] != "未提供":
                merged["experience_years"] = result["experience_years"]

            for skill in result.get("skills", []):
                if isinstance(skill, str):
                    normalized = self._normalize_skill_with_kb(skill.strip(), db)
                    if normalized:
                        skills_set.add(normalized)

            merged["work_experience"].extend(result.get("work_experience", []))
            merged["internship_experience"].extend(result.get("internship_experience", []))
            merged["education_history"].extend(result.get("education_history", []))

        for phrase in skill_phrases:
            skills_found = self._extract_skills_from_text(phrase, db)
            for skill in skills_found:
                skills_set.add(skill)

        merged["skills"] = list(skills_set)
        merged["skill_categories"] = self._categorize_skills(list(skills_set), db)

        skill_details = self._analyze_skills_with_market_data(list(skills_set), db)
        merged["hot_skills"] = skill_details["hot_skills"]
        merged["rare_skills"] = skill_details["rare_skills"]
        merged["skill_demand_info"] = skill_details["demand_info"]
        merged["skill_trend_info"] = skill_details["trend_info"]
        merged["skill_tags"] = skill_details["skill_tags"]

        return merged

    def _parse_standard(self, resume_text: str, db=None) -> dict:
        """标准解析方法"""
        try:
            prompt = get_resume_prompt(resume_text)
            response = self.qwen_client.chat(prompt)

            if response.get("success"):
                parsed_result = self.qwen_client.parse_json_response(response["content"])
                if parsed_result:
                    normalized = self._normalize_profile(parsed_result, db)
                    return normalized
        except Exception as e:
            logger.warning(f"AI resume parse failed, falling back: {e}")

        return self._parse_resume_fallback(resume_text, db)

    async def _parse_with_reasoning(self, resume_text: str, db=None) -> dict:
        """使用推理模式解析"""
        reasoning_context = f"""
        Resume to parse:
        {resume_text[:1000]}

        Please analyze and extract:
        1. Personal information (name, contact)
        2. Education background
        3. Work experience
        4. Technical skills
        5. Key achievements
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

        return self._parse_standard(resume_text, db)

    def _parse_reasoning_result(self, answer: str) -> Optional[Dict]:
        """解析推理结果"""
        try:
            if answer.strip().startswith("{"):
                return self._parse_json_with_fallback(answer)

            patterns = [
                r'"name":\s*"([^"]+)"',
                r'"skills":\s*\[([^\]]+)\]',
                r'"education":\s*"([^"]+)"',
                r'"experience":\s*"([^"]+)"',
            ]

            result = {}
            for pattern in patterns:
                match = re.search(pattern, answer)
                if match:
                    key = pattern.split('"')[1]
                    value = match.group(1)
                    if key == "skills":
                        result[key] = [s.strip().strip('"') for s in value.split(",")]
                    else:
                        result[key] = value

            return result if result else None
        except Exception as e:
            logger.warning(f"Failed to parse reasoning result: {e}")
            return None

    def _normalize_profile(self, parsed_result: dict, db=None) -> dict:
        """标准化简历档案"""
        skills = self._parse_skills(parsed_result.get("skills", []), db)
        skill_details = self._analyze_skills_with_market_data(skills, db)

        all_skills = set(skills)

        work_experience = parsed_result.get("work_experience", [])
        for exp in work_experience:
            if isinstance(exp, dict) and "technologies" in exp:
                for tech in exp.get("technologies", []):
                    if isinstance(tech, str):
                        normalized = self._normalize_skill_with_kb(tech.strip(), db)
                        if normalized:
                            all_skills.add(normalized)

        internship_experience = parsed_result.get("internship_experience", [])
        for exp in internship_experience:
            if isinstance(exp, dict) and "technologies" in exp:
                for tech in exp.get("technologies", []):
                    if isinstance(tech, str):
                        normalized = self._normalize_skill_with_kb(tech.strip(), db)
                        if normalized:
                            all_skills.add(normalized)

        normalized_work = self._normalize_experience(work_experience, db)
        normalized_internship = self._normalize_experience(internship_experience, db)

        return {
            "name": parsed_result.get("name", "未提供"),
            "phone": parsed_result.get("phone", "未提供"),
            "email": parsed_result.get("email", "未提供"),
            "education": parsed_result.get("education", "未提供"),
            "experience_years": parsed_result.get("experience_years", "未提供"),
            "skills": list(all_skills),
            "work_experience": normalized_work,
            "internship_experience": normalized_internship,
            "education_history": parsed_result.get("education_history", []),
            "self_evaluation": parsed_result.get("self_evaluation", ""),
            "highlights": parsed_result.get("highlights", []),
            "source": parsed_result.get("source", "ai"),
            "confidence": parsed_result.get("confidence", 0.8),
            "skill_categories": self._categorize_skills(list(all_skills), db),
            "hot_skills": skill_details["hot_skills"],
            "rare_skills": skill_details["rare_skills"],
            "skill_demand_info": skill_details["demand_info"],
            "skill_trend_info": skill_details["trend_info"],
            "skill_tags": skill_details["skill_tags"]
        }

    def _normalize_experience(self, experiences: list, db=None) -> list:
        """标准化工作/实习经历"""
        normalized = []
        for exp in experiences:
            if not isinstance(exp, dict):
                continue

            techs = []
            if "technologies" in exp:
                for tech in exp.get("technologies", []):
                    if isinstance(tech, str):
                        normalized_tech = self._normalize_skill_with_kb(tech.strip(), db)
                        if normalized_tech:
                            techs.append(normalized_tech)

            normalized.append({
                "company": exp.get("company", "未提供"),
                "position": exp.get("position", "未提供"),
                "duration": exp.get("duration", "未提供"),
                "description": exp.get("description", ""),
                "technologies": techs,
                "domain": exp.get("domain", "未提供")
            })

        return normalized

    def _analyze_skills_with_market_data(self, skills: List[str], db=None) -> Dict:
        """分析技能的市场数据"""
        hot_skills = []
        rare_skills = []
        demand_info = {}
        trend_info = {}

        try:
            for skill in skills:
                if db:
                    skill_info = self.knowledge_base.get_skill_info(skill, db=db)
                else:
                    skill_info = self.knowledge_base.get_skill_info(skill)

                if skill_info:
                    demand_weight = skill_info.get("demand_weight", 0)
                    avg_demand = skill_info.get("avg_demand", 0)
                    demand_info[skill] = {
                        "weight": demand_weight,
                        "avg_demand": avg_demand
                    }

                    trend = skill_info.get("demand_trend", 0)
                    trend_info[skill] = {
                        "trend": trend,
                        "trend_label": self._get_trend_label(trend)
                    }

                    if demand_weight > 0.002:
                        hot_skills.append({
                            "skill": skill,
                            "demand_weight": demand_weight,
                            "avg_demand": avg_demand
                        })

                    cooccurrence_count = skill_info.get("cooccurrence_count", 0)
                    if demand_weight > 0.0015 and cooccurrence_count < 100:
                        rare_skills.append({
                            "skill": skill,
                            "demand_weight": demand_weight,
                            "cooccurrence_count": cooccurrence_count
                        })

            hot_skills.sort(key=lambda x: x["demand_weight"], reverse=True)
            rare_skills.sort(key=lambda x: x["demand_weight"], reverse=True)

            skill_tags = {}
            hot_skill_names = {s["skill"] for s in hot_skills}
            rare_skill_names = {s["skill"] for s in rare_skills}

            for skill in skills:
                tags = []
                if skill in hot_skill_names:
                    tags.append("热门")
                if skill in rare_skill_names:
                    tags.append("稀缺")
                if skill in trend_info:
                    trend_label = trend_info[skill]["trend_label"]
                    if trend_label == "快速上升":
                        tags.append("上升")
                    elif trend_label == "快速下降":
                        tags.append("下降")

                skill_tags[skill] = tags

        except Exception as e:
            logger.error(f"Skill market data analysis failed: {e}", exc_info=True)
            skill_tags = {skill: [] for skill in skills}

        return {
            "hot_skills": hot_skills[:5],
            "rare_skills": rare_skills[:3],
            "demand_info": demand_info,
            "trend_info": trend_info,
            "skill_tags": skill_tags
        }

    def _parse_resume_fallback(self, resume_text: str, db=None) -> dict:
        """降级解析方法"""
        skills = self._extract_skills_from_text(resume_text, db)
        experience_years = self._extract_experience_years(resume_text)
        education = self._extract_education(resume_text)

        return {
            "name": self._extract_name(resume_text),
            "phone": self._extract_phone(resume_text),
            "email": self._extract_email(resume_text),
            "education": education,
            "experience_years": experience_years,
            "skills": skills,
            "work_experience": [],
            "education_history": [],
            "self_evaluation": "",
            "highlights": [],
            "source": "fallback",
            "confidence": 0.5,
            "skill_categories": self._categorize_skills(skills, db)
        }

    def _extract_name(self, text: str) -> str:
        """提取姓名"""
        patterns = [r'姓名[\s：:]([\u4e00-\u9fa5]{2,4})', r'name[\s：:]([\u4e00-\u9fa5]{2,4})']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "未提供"

    def _extract_phone(self, text: str) -> str:
        """提取电话"""
        match = re.search(r'1[3-9]\d{9}', text)
        return match.group() if match else "未提供"

    def _extract_email(self, text: str) -> str:
        """提取邮箱"""
        match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
        return match.group() if match else "未提供"

    def _extract_experience_years(self, text: str) -> str:
        """提取工作年限"""
        match = re.search(r'(\d+)\s*年[\s\S]*经验', text)
        if match:
            return f"{match.group(1)}年"
        return "未提供"

    def _extract_education(self, text: str) -> str:
        """提取学历"""
        edu_levels = ['博士', '硕士', '本科', '大专', '高中']
        for level in edu_levels:
            if level in text:
                return level
        return "未提供"

    def _get_empty_profile(self) -> dict:
        """获取空档案"""
        return {
            "name": "未提供",
            "phone": "未提供",
            "email": "未提供",
            "education": "未提供",
            "experience_years": "未提供",
            "skills": [],
            "work_experience": [],
            "education_history": [],
            "self_evaluation": "",
            "highlights": [],
            "source": "empty",
            "confidence": 0,
            "skill_categories": {}
        }

    def validate_profile(self, profile: dict) -> dict:
        """验证档案"""
        errors = []

        if not profile.get("name") or profile["name"] == "未提供":
            errors.append("缺少姓名信息")

        if not profile.get("phone") or profile["phone"] == "未提供":
            errors.append("缺少联系电话")

        if len(profile.get("skills", [])) == 0:
            errors.append("缺少技能信息")

        suggestions = []
        if len(profile.get("skills", [])) < 3:
            suggestions.append("建议补充更多技能信息以提高匹配准确性")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "suggestions": suggestions,
            "confidence": profile.get("confidence", 0)
        }

    def enrich_profile(self, profile: dict, db=None) -> dict:
        """丰富档案信息"""
        enriched = profile.copy()

        enriched_skills = []
        for skill in profile.get("skills", []):
            enriched_skill = {
                "skill": skill,
                "category": "unknown",
                "related_skills": [],
                "learning_difficulty": "medium"
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
            except Exception as e:
                logger.warning(f"Failed to enrich skill {skill}: {e}")

            enriched_skills.append(enriched_skill)

        enriched["skills_detail"] = enriched_skills
        enriched["skill_summary"] = {
            "total": len(enriched_skills),
            "by_category": self._summarize_by_category(enriched_skills)
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
