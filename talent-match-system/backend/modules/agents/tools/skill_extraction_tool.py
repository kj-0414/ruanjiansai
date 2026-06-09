"""
技能提取工具 - 使用专业NER模型（带降级方案）
基于transformers库的技能识别模型
"""

import time
from typing import Dict, Any, List, Set
from .base import BaseTool, ToolResult


class SkillExtractionTool(BaseTool):
    """基于NER模型的技能提取工具"""

    def __init__(self):
        super().__init__(
            name="extract_skills_ner",
            description="使用专业NER模型从文本中提取技术技能，支持中英文混合识别",
            parameters=[
                {"name": "text", "type": "string", "description": "输入文本", "required": True},
                {"name": "normalize", "type": "boolean", "description": "是否标准化技能名称", "required": False}
            ]
        )
        self.extractor = None
        self.kb_service = None
        self._extractor_initialized = False

    def _try_init_extractor(self):
        """尝试初始化NER提取器"""
        try:
            from transformers import pipeline
            self.extractor = pipeline(
                "token-classification",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            self.logger.info("NER extractor initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize NER extractor, using fallback: {e}")
            self.extractor = None

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

    async def execute(self, text: str, normalize: bool = True) -> ToolResult:
        start_time = time.time()

        try:
            kb = self._get_kb_service()

            skills = []
            
            if not self._extractor_initialized:
                self._try_init_extractor()
            
            if self.extractor is not None:
                skills = self._extract_with_ner(text)
            
            if not skills:
                skills = self._extract_with_keyword(text, kb)
            
            if normalize and kb is not None:
                skills = await self._normalize_skills(skills, kb)
            
            unique_skills = list(set(skills))

            return ToolResult(
                success=True,
                data={
                    "skills": [
                        {"name": s, "category": self._guess_category(s, kb)}
                        for s in unique_skills
                    ],
                    "count": len(unique_skills)
                },
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"Skill extraction failed: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def _extract_with_ner(self, text: str) -> List[str]:
        """使用NER模型提取技能"""
        if not self.extractor:
            return []
        
        try:
            result = self.extractor(text)
            
            skills = []
            for entity in result:
                if entity['entity_group'] in ['SKILL', 'TECH', 'ORG', 'PRODUCT']:
                    skills.append(entity['word'].strip())
            
            return skills
        except Exception as e:
            self.logger.warning(f"NER extraction failed: {e}")
            return []

    def _extract_with_keyword(self, text: str, kb=None) -> List[str]:
        """使用关键词匹配提取技能（降级方案）"""
        text_lower = text.lower()
        found_skills = []

        tech_keywords = [
            'Python', 'Java', 'C++', 'C#', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'PHP', 'Ruby',
            'Swift', 'Kotlin', 'Objective-C', 'Scala', 'Perl', 'Lua', 'R', 'MATLAB',
            'HTML', 'CSS', 'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server',
            'Linux', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', '阿里云', '腾讯云',
            'Git', 'Jenkins', 'CI/CD', 'Nginx', 'Apache', 'Tomcat',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
            'NLP', 'Computer Vision', 'Data Analysis', 'Big Data', 'Hadoop', 'Spark',
            'Android', 'iOS', 'Flutter', 'React Native', 'WeChat Mini Program',
            'Photoshop', 'Illustrator', 'Figma', 'Sketch', 'Axure',
            '项目管理', '团队协作', '沟通能力', '问题解决'
        ]

        for skill in tech_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        if kb:
            all_skills = kb.db.get_all_skills()
            for skill in all_skills:
                skill_name = skill.get('skill_name', '').lower()
                if skill_name in text_lower and skill_name not in [s.lower() for s in found_skills]:
                    found_skills.append(skill.get('skill_name'))

                aliases_text = skill.get('skill_aliases', '[]')
                try:
                    import json
                    aliases = json.loads(aliases_text)
                    for alias in aliases:
                        if alias.lower() in text_lower and skill.get('skill_name') not in found_skills:
                            found_skills.append(skill.get('skill_name'))
                            break
                except:
                    pass

        return found_skills

    async def _normalize_skills(self, skills: List[str], kb) -> List[str]:
        """标准化技能名称"""
        if not kb:
            return skills

        normalized = []
        for skill in skills:
            try:
                result = kb.normalize_skill(skill)
                if result and result.get('normalized_name'):
                    normalized.append(result['normalized_name'])
                else:
                    normalized.append(skill)
            except:
                normalized.append(skill)

        return normalized

    def _guess_category(self, skill: str, kb) -> str:
        """猜测技能类别"""
        if kb:
            try:
                skill_info = kb.get_skill_info(skill)
                if skill_info and skill_info.get('category'):
                    return skill_info['category']
            except:
                pass

        frontend_keywords = ['vue', 'react', 'angular', 'html', 'css', 'javascript', 'typescript']
        backend_keywords = ['java', 'python', 'go', 'spring', 'django', 'flask', 'node']
        database_keywords = ['mysql', 'postgresql', 'mongodb', 'redis', 'sql']
        devops_keywords = ['docker', 'kubernetes', 'jenkins', 'git', 'ci/cd']
        ai_keywords = ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp']

        skill_lower = skill.lower()
        
        if any(k in skill_lower for k in frontend_keywords):
            return '前端开发'
        elif any(k in skill_lower for k in backend_keywords):
            return '后端开发'
        elif any(k in skill_lower for k in database_keywords):
            return '数据库'
        elif any(k in skill_lower for k in devops_keywords):
            return 'DevOps'
        elif any(k in skill_lower for k in ai_keywords):
            return '人工智能'
        
        return '其他'


skill_extraction_tool = SkillExtractionTool()