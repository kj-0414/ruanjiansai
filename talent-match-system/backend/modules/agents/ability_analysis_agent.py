import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.qwen_client import get_qwen_client

logger = logging.getLogger(__name__)

try:
    from modules.agents.knowledge_base_agent import KnowledgeBaseAgent
    KB_AVAILABLE = True
except ImportError:
    KB_AVAILABLE = False
    logger.warning("知识库模块未找到，将使用默认分类")

class AbilityAnalysisAgent:
    """
    能力分析智能体
    负责生成个人能力树状图、五维雷达图、文本分析报告
    """
    
    def __init__(self):
        self.qwen_client = get_qwen_client()
        self.kb_agent = KnowledgeBaseAgent() if KB_AVAILABLE else None
        self._kb_categories_cache = None
    
    def analyze_ability(self, resume_data: Dict[str, Any], user_id: str, resume_id: Optional[str] = None) -> Dict[str, Any]:
        """
        综合能力分析入口
        返回能力树、雷达图、文本分析等完整数据
        """
        logger.info(f"开始分析用户 {user_id} 的能力")
        
        result = {
            "ability_tree": self._generate_ability_tree(resume_data),
            "radar_chart": self._generate_radar_chart(resume_data),
            "text_analysis": self._generate_text_analysis(resume_data),
            "analysis_time": datetime.now().isoformat()
        }
        
        return result
    
    def _generate_ability_tree(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成个人能力树状图
        """
        # 从简历数据中提取信息
        skills = resume_data.get("skills", [])
        work_experience = resume_data.get("work_experience", [])
        project_experience = resume_data.get("projects", [])
        internship_experience = resume_data.get("internship_experience", [])
        certificates = resume_data.get("certificates", [])
        honors = resume_data.get("honors", [])
        
        # 构建实践经历子节点
        practice_children = []
        
        # 添加工作经历
        work_tree = self._build_experience_tree(work_experience)
        if work_tree:
            practice_children.append({
                "name": "工作经历",
                "children": work_tree
            })
        
        # 添加实习经历
        internship_tree = self._build_internship_tree(internship_experience)
        if internship_tree:
            practice_children.append({
                "name": "实习经历",
                "children": internship_tree
            })
        
        # 添加项目经历
        project_tree = self._build_project_tree(project_experience)
        if project_tree:
            practice_children.append({
                "name": "项目经历",
                "children": project_tree
            })
        
        # 构建能力树结构
        ability_tree = {
            "name": "个人能力",
            "children": []
        }
        
        # 添加教育背景节点
        education_tree = self._build_education_tree(resume_data)
        if education_tree:
            ability_tree["children"].append({
                "name": "教育背景",
                "children": education_tree,
                "weight": 0.15,
                "match_type": "semantic"
            })
        
        # 添加技能节点
        skill_tree = self._build_skill_category_tree(skills)
        if skill_tree:
            ability_tree["children"].append({
                "name": "技能",
                "children": skill_tree,
                "weight": 0.4,
                "match_type": "semantic"
            })
        
        # 添加实践经历节点（有子节点才添加）
        if practice_children:
            ability_tree["children"].append({
                "name": "实践经历",
                "children": practice_children,
                "weight": 0.3,
                "match_type": "semantic"
            })
        
        # 添加获奖荣誉节点
        honors_tree = self._build_honors_tree(honors, certificates)
        if honors_tree:
            ability_tree["children"].append({
                "name": "获奖荣誉",
                "children": honors_tree,
                "weight": 0.15,
                "match_type": "semantic"
            })
        
        return ability_tree
    
    def _build_skill_category_tree(self, skills: list) -> list:
        """
        构建技能分类树
        优先使用知识库进行智能分类，降级到默认规则
        """
        if self.kb_agent:
            return self._build_skill_category_tree_with_kb(skills)
        return self._build_skill_category_tree_fallback(skills)
    
    def _build_skill_category_tree_with_kb(self, skills: list) -> list:
        """
        使用知识库构建技能分类树
        """
        try:
            normalized = self.kb_agent.normalize_skills(skills)
            category_tree = {}
            
            for item in normalized:
                skill_name = item['normalized']
                confidence = item.get('confidence', 0)
                
                if confidence > 0:
                    skill_info = self.kb_agent.query_skill(skill_name)
                    if skill_info.get('found') and skill_info.get('data'):
                        category = skill_info['data'].get('category', '其他技能')
                        category = self._get_kb_category_name(category)
                    else:
                        category = self._infer_category_from_kb(skill_name)
                else:
                    category = self._infer_category_from_kb(skill_name)
                
                if category not in category_tree:
                    category_tree[category] = []
                category_tree[category].append({"name": skill_name, "confidence": confidence})
            
            return [{"name": cat, "children": children} for cat, children in category_tree.items()]
        except Exception as e:
            logger.error(f"使用知识库分类失败，降级到默认规则: {e}")
            return self._build_skill_category_tree_fallback(skills)
    
    def _infer_category_from_kb(self, skill_name: str) -> str:
        """
        从知识库推断技能分类
        """
        if not self.kb_agent:
            return "其他技能"
        
        try:
            recommendations = self.kb_agent.recommend_skills([skill_name], limit=3)
            if recommendations:
                first_rec = recommendations[0]
                related_skill = first_rec.get('skill_name', '')
                related_info = self.kb_agent.query_skill(related_skill)
                if related_info.get('found') and related_info.get('data'):
                    return related_info['data'].get('category', '其他技能')
        except Exception:
            pass
        
        return self._get_default_category(skill_name)
    
    def _get_kb_category_name(self, category: str) -> str:
        """
        将知识库分类名称映射为更友好的显示名称
        """
        category_mapping = {
            "编程语言": "编程语言",
            "前端技术": "前端技术",
            "后端框架": "后端框架",
            "数据库": "数据库",
            "大数据": "大数据",
            "机器学习/AI": "人工智能",
            "DevOps/云计算": "DevOps/云计算",
            "云服务": "云服务",
            "版本控制/协作": "版本控制",
            "移动开发": "移动开发",
            "测试": "测试",
            "安全": "安全",
            "网络/协议": "网络技术",
            "软件工程/方法论": "软件工程",
            "数据分析/可视化": "数据分析",
            "UI/UX设计": "UI/UX设计",
            "其他/通用技能": "其他技能"
        }
        return category_mapping.get(category, category)
    
    def _get_default_category(self, skill_name: str) -> str:
        """
        默认分类规则（降级方案）
        """
        skill_lower = str(skill_name).lower()
        categories = {
            "前端开发": ["vue", "react", "javascript", "typescript", "html", "css", "webpack", "angular", "svelte", "vite"],
            "后端开发": ["python", "java", "go", "node", "nodejs", "mysql", "postgresql", "redis", "mongodb", "spring", "django", "flask"],
            "移动开发": ["android", "ios", "flutter", "react native", "uniapp", "swift", "kotlin"],
            "数据处理": ["pandas", "numpy", "spark", "hadoop", "hive", "sql"],
            "人工智能": ["tensorflow", "pytorch", "机器学习", "深度学习", "nlp", "计算机视觉", "cv", "transformer"],
            "云与运维": ["docker", "kubernetes", "k8s", "jenkins", "aws", "阿里云", "华为云", "腾讯云", "devops"],
            "数据库": ["mysql", "postgresql", "redis", "mongodb", "oracle", "达梦", "sqlite"],
            "测试": ["自动化测试", "单元测试", "selenium", "pytest", "jmeter"],
            "安全": ["网络安全", "渗透测试", "安全开发", "cryptography"],
            "工具": ["git", "github", "gitlab", "vs code", "idea"]
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in skill_lower:
                    return category
        
        return "其他技能"
    
    def _build_skill_category_tree_fallback(self, skills: list) -> list:
        """
        降级方案：使用扩展的默认分类规则
        """
        category_tree = {}
        
        for skill in skills:
            category = self._get_default_category(skill)
            if category not in category_tree:
                category_tree[category] = []
            category_tree[category].append({"name": str(skill)})
        
        return [{"name": cat, "children": children} for cat, children in category_tree.items()]
    
    def _build_certificate_tree(self, certificates: list) -> list:
        """
        构建证书树
        """
        tree = []
        for cert in certificates:
            if isinstance(cert, dict):
                tree.append({"name": cert.get("name", "未知证书")})
            else:
                tree.append({"name": str(cert)})
        return tree
    
    def _build_experience_tree(self, experiences: list) -> list:
        """
        构建工作经历树
        """
        tree = []
        for exp in experiences:
            if isinstance(exp, dict):
                company = exp.get("company", "未知公司")
                position = exp.get("position", "未知职位")
                tree.append({
                    "name": f"{company} - {position}",
                    "children": [
                        {"name": exp.get("description", "无描述")[:50] + "..."}
                    ]
                })
        return tree
    
    def _build_project_tree(self, projects: list) -> list:
        """
        构建项目经历树
        """
        tree = []
        for proj in projects:
            if isinstance(proj, dict):
                name = proj.get("name", "未知项目")
                domain = proj.get("domain", "未知领域")
                tree.append({
                    "name": f"{name} - {domain}",
                    "children": [
                        {"name": proj.get("description", "无描述")[:50] + "..."}
                    ]
                })
            elif isinstance(proj, str) and proj.strip():
                tree.append({"name": proj})
        return tree
    
    def _build_education_tree(self, resume_data: Dict[str, Any]) -> list:
        """
        构建教育背景树
        """
        tree = []
        education_items = []
        
        # 提取教育信息
        school = resume_data.get("school", "")
        major = resume_data.get("major", "")
        degree = resume_data.get("degree", "")
        education = resume_data.get("education", "")
        
        # 构建教育信息
        edu_parts = []
        if school:
            edu_parts.append(f"学校: {school}")
        if major:
            edu_parts.append(f"专业: {major}")
        if degree:
            edu_parts.append(f"学历: {degree}")
        if education and education not in edu_parts:
            edu_parts.append(education)
        
        if edu_parts:
            education_items.append({
                "name": " | ".join(edu_parts)
            })
        
        return education_items
    
    def _build_internship_tree(self, internships: list) -> list:
        """
        构建实习经历树
        """
        tree = []
        for internship in internships:
            if isinstance(internship, dict):
                company = internship.get("company", "未知公司")
                position = internship.get("position", "未知职位")
                tree.append({
                    "name": f"{company} - {position}",
                    "children": [
                        {"name": internship.get("description", "无描述")[:50] + "..."}
                    ]
                })
            elif isinstance(internship, str) and internship.strip():
                tree.append({"name": internship})
        return tree
    
    def _build_honors_tree(self, honors: list, certificates: list) -> list:
        """
        构建获奖荣誉树（包含证书）
        """
        tree = []
        
        # 添加获奖荣誉
        for honor in honors:
            if isinstance(honor, dict):
                tree.append({"name": honor.get("name", "未知荣誉")})
            elif isinstance(honor, str) and honor.strip():
                tree.append({"name": honor})
        
        # 添加证书
        for cert in certificates:
            if isinstance(cert, dict):
                tree.append({"name": cert.get("name", "未知证书")})
            elif isinstance(cert, str) and cert.strip():
                tree.append({"name": cert})
        
        return tree
    
    def _generate_radar_chart(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成五维雷达图数据
        """
        # 先从简历数据中提取关键信息
        education = resume_data.get("education", "")
        skills = resume_data.get("skills", [])
        certificates = resume_data.get("certificates", [])
        work_experience = resume_data.get("work_experience", [])
        project_experience = resume_data.get("projects", [])
        
        # 评分函数
        def calculate_education_score(edu_text: str) -> int:
            edu_lower = str(edu_text).lower()
            if "博士" in edu_lower or "phd" in edu_lower:
                return 100
            elif "硕士" in edu_lower or "master" in edu_lower:
                return 90
            elif "本科" in edu_lower or "bachelor" in edu_lower:
                return 80
            elif "大专" in edu_lower or "associate" in edu_lower:
                return 70
            elif "高中" in edu_lower:
                return 50
            return 60  # 默认
        
        def calculate_skills_score(skills_list: list) -> int:
            if not skills_list:
                return 50
            score = min(100, 50 + len(skills_list) * 5)
            return score
        
        def calculate_certificates_score(certs_list: list) -> int:
            if not certs_list:
                return 50
            score = min(100, 50 + len(certs_list) * 10)
            return score
        
        def calculate_experience_score(exp_list: list) -> int:
            if not exp_list:
                return 50
            # 简单计算：工作经历数量 + 描述长度
            score = 50
            for exp in exp_list:
                if isinstance(exp, dict):
                    desc = exp.get("description", "")
                    if len(str(desc)) > 100:
                        score += 15
                    score += 10
            return min(100, score)
        
        def calculate_project_score(proj_list: list) -> int:
            if not proj_list:
                return 50
            score = 50
            for proj in proj_list:
                if isinstance(proj, dict):
                    desc = proj.get("description", "")
                    if len(str(desc)) > 50:
                        score += 15
                    score += 10
            return min(100, score)
        
        scores = {
            "education": calculate_education_score(education),
            "skills": calculate_skills_score(skills),
            "certificates": calculate_certificates_score(certificates),
            "work_experience": calculate_experience_score(work_experience),
            "project_experience": calculate_project_score(project_experience)
        }
        
        return {
            "dimensions": ["学历背景", "专业技能", "证书资质", "工作经验", "项目经历"],
            "values": [
                scores["education"],
                scores["skills"],
                scores["certificates"],
                scores["work_experience"],
                scores["project_experience"]
            ],
            "details": {
                "education": {"score": scores["education"], "description": self._get_education_description(education)},
                "skills": {"score": scores["skills"], "description": self._get_skills_description(skills)},
                "certificates": {"score": scores["certificates"], "description": self._get_certificate_description(certificates)},
                "work_experience": {"score": scores["work_experience"], "description": self._get_experience_description(work_experience)},
                "project_experience": {"score": scores["project_experience"], "description": self._get_project_description(project_experience)}
            }
        }
    
    def _get_education_description(self, education: str) -> str:
        if not education or education == "未提供":
            return "待完善教育背景信息"
        return f"最高学历: {education}"
    
    def _get_skills_description(self, skills: list) -> str:
        if not skills:
            return "暂无技能信息"
        return f"掌握 {len(skills)} 项技能"
    
    def _get_certificate_description(self, certificates: list) -> str:
        if not certificates:
            return "暂无证书信息"
        return f"持有 {len(certificates)} 项证书"
    
    def _get_experience_description(self, experiences: list) -> str:
        if not experiences:
            return "暂无工作经验"
        return f"有 {len(experiences)} 段工作经历"
    
    def _get_project_description(self, projects: list) -> str:
        if not projects:
            return "暂无项目经验"
        return f"参与过 {len(projects)} 个项目"
    
    def _generate_text_analysis(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成文本分析报告（使用LLM）
        """
        resume_text = self._format_resume_for_llm(resume_data)
        
        try:
            prompt = f"""请分析以下简历，并根据简历中提到的意向岗位/目标职位生成针对性的发展建议，输出JSON格式：

简历：
{resume_text}

输出格式：
{{
    "industry": "IT互联网",
    "target_position": "前端开发工程师",
    "overview": "具备扎实的前端开发能力，熟悉Vue3等主流框架，有企业实习经验",
    "strengths": ["精通Vue3、Element Plus等前端技术栈", "具备实际项目开发经验", "熟悉国产化系统适配"],
    "weaknesses": ["缺乏大型项目独立开发经验", "证书认证不足"],
    "suggestions": ["建议考取前端开发相关认证，如华为HCIA或AWS云从业者认证，增强专业竞争力", "参与开源项目或独立开发个人项目，积累项目经验和作品集", "深入学习国产化技术栈，如银河麒麟系统适配，提升技术广度"],
    "dimensions": {{
        "education": {{"score": 85, "desc": "学历分析"}},
        "skills": {{"score": 78, "desc": "技能水平"}},
        "certificates": {{"score": 60, "desc": "证书情况"}},
        "experience": {{"score": 80, "desc": "工作经验"}},
        "projects": {{"score": 75, "desc": "项目经历"}}
    }}
}}

规则：
1. industry：识别简历所属行业（IT互联网/金融/教育/医疗/制造/销售等）
2. target_position：从简历中识别意向岗位或目标职位，如果未明确提及则填空字符串
3. overview：一句话总结核心竞争力，突出与意向岗位的匹配度
4. strengths：3-4条具体优势，结合意向岗位说明，每条优势不超过20字
5. weaknesses：1-2条真实短板，结合意向岗位说明差距，每条不超过20字
6. suggestions：3条可执行建议，必须紧密围绕意向岗位需求，针对性强
7. 每条suggestions必须是独立完整的句子，以句号结尾，长度50-80字
8. suggestions中绝对不要使用顿号分隔多条内容，每条建议只包含一个核心行动
9. dimensions：五个维度打分0-100，desc简洁描述，不超过20字
10. 语言专业简洁，避免空话"""

            response = self.qwen_client.chat(prompt)
            
            if response.get("success"):
                parsed_result = self.qwen_client.parse_json_response(response["content"])
                if parsed_result:
                    return self._format_text_analysis_result(parsed_result)
        except Exception as e:
            logger.warning(f"LLM分析失败，使用默认分析: {e}")
        
        # 降级方案：使用简单规则生成
        return self._get_default_text_analysis(resume_data)
    
    def _format_resume_for_llm(self, resume_data: Dict[str, Any]) -> str:
        """
        将简历数据格式化为LLM可读的文本
        """
        lines = []
        
        if resume_data.get("name"):
            lines.append(f"姓名: {resume_data['name']}")
        if resume_data.get("education"):
            lines.append(f"教育背景: {resume_data['education']}")
        if resume_data.get("school"):
            lines.append(f"毕业院校: {resume_data['school']}")
        if resume_data.get("major"):
            lines.append(f"专业: {resume_data['major']}")
        
        skills = resume_data.get("skills", [])
        if skills:
            lines.append(f"技能: {', '.join([str(s) for s in skills])}")
        
        work_exp = resume_data.get("work_experience", [])
        if work_exp:
            lines.append("工作经历:")
            for exp in work_exp:
                if isinstance(exp, dict):
                    lines.append(f"  - {exp.get('company', '')}: {exp.get('position', '')}")
        
        projects = resume_data.get("projects", [])
        if projects:
            lines.append("项目经历:")
            for proj in projects:
                if isinstance(proj, dict):
                    lines.append(f"  - {proj.get('name', '')}: {proj.get('domain', '')}")
        
        return "\n".join(lines)
    
    def _format_text_analysis_result(self, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化文本分析结果以适配前端
        """
        strengths = parsed_result.get("strengths", [])
        weaknesses = parsed_result.get("weaknesses", [])
        suggestions = parsed_result.get("suggestions", [])
        
        # 转换为前端期望的格式
        if isinstance(strengths, list):
            advantages_str = "、".join(strengths) + "。" if strengths else "暂无明显优势。"
        else:
            advantages_str = str(strengths) if strengths else "暂无明显优势。"
        
        if isinstance(weaknesses, list):
            disadvantages_str = "、".join(weaknesses) + "。" if weaknesses else "暂无明显劣势。"
        else:
            disadvantages_str = str(weaknesses) if weaknesses else "暂无明显劣势。"
        
        if isinstance(suggestions, list):
            cleaned_suggestions = [s.rstrip('。').strip() for s in suggestions if s.strip()]
            suggestions_str = "、".join(cleaned_suggestions) if cleaned_suggestions else "建议继续保持和提升现有能力。"
        else:
            suggestions_str = str(suggestions).rstrip('。').strip() if suggestions else "建议继续保持和提升现有能力。"
        
        result = {
            "advantages": advantages_str,
            "disadvantages": disadvantages_str,
            "suggestions": suggestions_str,
            "industry": parsed_result.get("industry", ""),
            "overview": parsed_result.get("overview", ""),
            "dimensions": self._extract_dimensions_from_analysis(parsed_result)
        }
        
        return result
    
    def _extract_dimensions_from_analysis(self, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从分析结果中提取维度信息
        """
        dimensions = parsed_result.get("dimensions", {})
        
        return {
            "education": {
                "score": dimensions.get("education", {}).get("score", 0),
                "description": dimensions.get("education", {}).get("desc", "") or dimensions.get("education", {}).get("description", "待分析")
            },
            "skills": {
                "score": dimensions.get("skills", {}).get("score", 0),
                "description": dimensions.get("skills", {}).get("desc", "") or dimensions.get("skills", {}).get("description", "待分析")
            },
            "certificates": {
                "score": dimensions.get("certificates", {}).get("score", 0),
                "description": dimensions.get("certificates", {}).get("desc", "") or dimensions.get("certificates", {}).get("description", "待分析")
            },
            "work_experience": {
                "score": dimensions.get("experience", {}).get("score", 0) or dimensions.get("work_experience", {}).get("score", 0),
                "description": dimensions.get("experience", {}).get("desc", "") or dimensions.get("work_experience", {}).get("description", "待分析")
            },
            "project_experience": {
                "score": dimensions.get("projects", {}).get("score", 0) or dimensions.get("project_experience", {}).get("score", 0),
                "description": dimensions.get("projects", {}).get("desc", "") or dimensions.get("project_experience", {}).get("description", "待分析")
            }
        }
    
    def _get_default_text_analysis(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取默认文本分析（降级方案）
        """
        skills_count = len(resume_data.get("skills", []))
        exp_count = len(resume_data.get("work_experience", []))
        proj_count = len(resume_data.get("projects", []))
        
        return {
            "advantages": f"掌握{skills_count}项技能，有{exp_count}段工作经历，参与{proj_count}个项目。",
            "disadvantages": "建议补充更多技能认证信息。",
            "suggestions": "建议继续积累项目经验，提升技术能力。",
            "industry": "",
            "overview": "",
            "dimensions": {
                "education": {"score": 0, "description": "待分析"},
                "skills": {"score": 0, "description": "待分析"},
                "certificates": {"score": 0, "description": "待分析"},
                "work_experience": {"score": 0, "description": "待分析"},
                "project_experience": {"score": 0, "description": "待分析"}
            }
        }
