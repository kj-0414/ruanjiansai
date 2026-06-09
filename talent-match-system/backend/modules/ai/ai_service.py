from models import Resume, AIResumeParse, AbilityAnalysisCache
import json
from copy import deepcopy
from datetime import datetime, timedelta
from utils.qwen_client import get_qwen_client

class AIService:
    def __init__(self):
        self.qwen_client = get_qwen_client()
        
        # 预设框架结构（保持与前端一致）
        self.ABILITY_TREE_FRAMEWORK = {
            "name": "个人能力",
            "children": []
        }
    
    async def get_ai(self, db):
        return []
    
    def _get_cache(self, user_id, analysis_type, db, resume_id=None):
        """从缓存获取分析结果（有效期24小时）"""
        query = db.query(AbilityAnalysisCache).filter(
            AbilityAnalysisCache.user_id == user_id,
            AbilityAnalysisCache.analysis_type == analysis_type
        )
        if resume_id:
            query = query.filter(AbilityAnalysisCache.resume_id == resume_id)
        
        cache = query.first()
        
        if cache:
            # 检查缓存是否过期（24小时）
            if cache.updated_at and datetime.now() - cache.updated_at < timedelta(hours=24):
                try:
                    return json.loads(cache.result)
                except:
                    pass
        return None
    
    def _set_cache(self, user_id, analysis_type, result, db, resume_id=None):
        """保存分析结果到缓存"""
        try:
            query = db.query(AbilityAnalysisCache).filter(
                AbilityAnalysisCache.user_id == user_id,
                AbilityAnalysisCache.analysis_type == analysis_type
            )
            if resume_id:
                query = query.filter(AbilityAnalysisCache.resume_id == resume_id)
            
            cache = query.first()
            now = datetime.now()
            
            if cache:
                cache.result = json.dumps(result)
                cache.updated_at = now
            else:
                new_cache = AbilityAnalysisCache(
                    user_id=user_id,
                    resume_id=resume_id,
                    analysis_type=analysis_type,
                    result=json.dumps(result),
                    created_at=now,
                    updated_at=now
                )
                db.add(new_cache)
            
            db.commit()
            print(f"[AI Service] 缓存保存成功: user_id={user_id}, analysis_type={analysis_type}")
        except Exception as e:
            print(f"[AI Service] 缓存保存失败（外键约束或其他错误）: {e}")
            db.rollback()
    
    def _get_resume_text(self, user_id, db, resume_id=None):
        """获取简历文本内容（支持通过user_id或resume_id查询）"""
        if resume_id:
            # 如果提供了简历ID，直接查询该简历
            # 确保 resume_id 转换为整数类型
            try:
                resume_id_int = int(resume_id)
            except (ValueError, TypeError):
                resume_id_int = None
            
            if resume_id_int:
                resumes = db.query(Resume).filter(Resume.id == resume_id_int).all()
                ai_resume_parses = db.query(AIResumeParse).filter(AIResumeParse.resume_id == resume_id_int).all()
            else:
                resumes = []
                ai_resume_parses = []
        else:
            # 否则按用户ID查询
            resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
            ai_resume_parses = db.query(AIResumeParse).filter(AIResumeParse.user_id == user_id).all()
        
        text_parts = []
        
        for resume in resumes:
            if resume.name:
                text_parts.append(f"姓名: {resume.name}")
            if resume.education or resume.school or resume.major or resume.degree:
                edu_info = []
                if resume.school:
                    edu_info.append(f"学校: {resume.school}")
                if resume.major:
                    edu_info.append(f"专业: {resume.major}")
                if resume.degree:
                    edu_info.append(f"学历: {resume.degree}")
                if resume.education:
                    edu_info.append(f"教育背景: {resume.education}")
                if edu_info:
                    text_parts.append("; ".join(edu_info))
            if resume.experience:
                text_parts.append(f"工作经历: {resume.experience}")
            if resume.skills:
                text_parts.append(f"技能: {resume.skills}")
            if resume.self_evaluation:
                text_parts.append(f"自我评价: {resume.self_evaluation}")
            # 提取项目经历
            if getattr(resume, "projects", None):
                text_parts.append(f"项目经历: {resume.projects}")
            # 提取工作经验详情
            if getattr(resume, "work_experience", None):
                text_parts.append(f"工作经验详情: {resume.work_experience}")
            # 提取证书信息
            if getattr(resume, "certificates", None):
                text_parts.append(f"证书: {resume.certificates}")
            # 提取技能详情
            if getattr(resume, "skills_detail", None):
                text_parts.append(f"技能详情: {resume.skills_detail}")
        
        for parse in ai_resume_parses:
            if parse.parsed_result:
                text_parts.append(f"AI解析结果: {parse.parsed_result}")
            if parse.raw_text:
                text_parts.append(f"原始文本: {parse.raw_text}")
        
        return "\n".join(text_parts) if text_parts else "暂无简历信息"
    
    def get_ability_tree(self, user_id, db, resume_id=None):
        """使用AI按预设框架提取技能并构建能力树"""
        
        # 先尝试从缓存获取
        cached_result = self._get_cache(user_id, "ability_tree", db, resume_id)
        if cached_result:
            print(f"[AI Service] 从缓存获取能力树，用户: {user_id}")
            return cached_result
        
        resume_text = self._get_resume_text(user_id, db, resume_id)
        
        print(f"[AI Service] 用户 {user_id} 的简历文本长度: {len(resume_text)}")
        print(f"[AI Service] 简历文本内容: {resume_text[:500]}...")
        
        # 如果没有简历数据，返回默认框架
        if resume_text == "暂无简历信息":
            print("[AI Service] 没有找到简历数据，使用默认能力树")
            return self._get_default_ability_tree()
        
        # 使用AI提取信息
        print("[AI Service] 开始调用Qwen AI分析简历...")
        prompt = f"""请从以下简历文本中提取信息，按照指定框架组织：

简历文本：
{resume_text}

请严格按照以下结构返回JSON格式数据：
{{
    "教育背景": ["学校: 北京大学|专业: 计算机科学与技术|学历: 本科"],
    "技能": ["前端开发: Vue.js, React, JavaScript", "后端开发: Node.js, Python", "数据库: MySQL, MongoDB", "工具技能: Git, Docker"],
    "工作经历": ["2022-至今: XX公司 - 前端开发工程师"],
    "实习经历": ["2021-2022: YY公司 - 实习生"],
    "项目经历": ["项目名称1|技术栈: Vue.js, Node.js|领域: 企业管理", "项目名称2|技术栈: React, Python|领域: 电商"],
    "获奖荣誉": ["奖项名称1", "证书名称1", "奖项名称2"]
}}

要求：
1. 每个类别至少提取1条信息，如果没有相关信息则为空数组
2. 技能请按照"前端开发"、"后端开发"、"数据库"、"工具技能"等分类提取
3. 项目经历请按照"项目名称|技术栈: xxx|领域: xxx"格式提取
4. 获奖荣誉包含奖项和证书
5. 保持格式简洁，不要添加额外内容
6. 确保JSON格式正确，可以被解析"""
        
        response = self.qwen_client.chat(prompt)
        print(f"[AI Service] AI响应状态: {response.get('success')}")
        
        if response["success"]:
            print(f"[AI Service] AI响应内容: {response.get('content')[:500]}...")
            parsed_result = self.qwen_client.parse_json_response(response["content"])
            print(f"[AI Service] 解析后的JSON: {parsed_result}")
            if parsed_result:
                print("[AI Service] 使用AI分析结果构建能力树")
                result = self._build_ability_tree_from_ai(parsed_result)
                # 保存到缓存
                self._set_cache(user_id, "ability_tree", result, db, resume_id)
                return result
        
        # 如果AI调用失败，返回默认框架
        print("[AI Service] AI调用失败或解析失败，使用默认能力树")
        return self._get_default_ability_tree()
    
    def _build_ability_tree_from_ai(self, ai_result):
        """根据AI结果构建能力树"""
        ability_tree = deepcopy(self.ABILITY_TREE_FRAMEWORK)
        
        # 构建实践经历子节点
        practice_children = []
        
        # 添加教育背景
        if "教育背景" in ai_result and ai_result["教育背景"]:
            education_items = ai_result["教育背景"]
            ability_tree["children"].append({
                "name": "教育背景",
                "children": [{"name": item} for item in education_items if item.strip()],
                "weight": 0.15,
                "match_type": "semantic"
            })
        
        # 添加技能
        if "技能" in ai_result and ai_result["技能"]:
            skill_items = ai_result["技能"]
            skill_children = []
            for item in skill_items:
                if item.strip():
                    skill_children.append(self._parse_skill_item(item))
            if skill_children:
                ability_tree["children"].append({
                    "name": "技能",
                    "children": skill_children,
                    "weight": 0.4,
                    "match_type": "semantic"
                })
        
        # 添加工作经历
        if "工作经历" in ai_result and ai_result["工作经历"]:
            work_items = ai_result["工作经历"]
            practice_children.append({
                "name": "工作经历",
                "children": [{"name": item} for item in work_items if item.strip()]
            })
        
        # 添加实习经历
        if "实习经历" in ai_result and ai_result["实习经历"]:
            internship_items = ai_result["实习经历"]
            practice_children.append({
                "name": "实习经历",
                "children": [{"name": item} for item in internship_items if item.strip()]
            })
        
        # 添加项目经历
        if "项目经历" in ai_result and ai_result["项目经历"]:
            project_items = ai_result["项目经历"]
            project_children = [self._parse_project_item(item) for item in project_items if item.strip()]
            practice_children.append({
                "name": "项目经历",
                "children": project_children
            })
        
        # 添加实践经历
        if practice_children:
            ability_tree["children"].append({
                "name": "实践经历",
                "children": practice_children,
                "weight": 0.3,
                "match_type": "semantic"
            })
        
        # 添加获奖荣誉
        if "获奖荣誉" in ai_result and ai_result["获奖荣誉"]:
            honor_items = ai_result["获奖荣誉"]
            ability_tree["children"].append({
                "name": "获奖荣誉",
                "children": [{"name": item} for item in honor_items if item.strip()],
                "weight": 0.15,
                "match_type": "semantic"
            })
        
        return ability_tree
    
    def _parse_project_item(self, item):
        """解析项目经历条目"""
        parts = item.split("|")
        result = {"name": ""}
        children = []
        
        for part in parts:
            part = part.strip()
            if "技术栈:" in part:
                tech_stack = part.replace("技术栈:", "").strip()
                children.append({"name": "技术栈: " + tech_stack})
            elif "领域:" in part:
                domain = part.replace("领域:", "").strip()
                children.append({"name": "领域: " + domain})
            elif result["name"] == "":
                result["name"] = part
        
        if children:
            result["children"] = children
        
        return result
    
    def _parse_skill_item(self, item):
        """解析专业技能条目"""
        if ":" in item:
            category, skills = item.split(":", 1)
            return {
                "name": category.strip(),
                "children": [{"name": s.strip()} for s in skills.split(",") if s.strip()]
            }
        return {"name": item}
    
    def _get_default_ability_tree(self):
        """获取空的能力树（没有数据时返回空结构）"""
        return deepcopy(self.ABILITY_TREE_FRAMEWORK)
    
    def get_ability_radar(self, user_id, db, resume_id=None):
        """使用AI分析五维图谱数据"""
        
        # 先尝试从缓存获取
        cached_result = self._get_cache(user_id, "ability_radar", db, resume_id)
        if cached_result:
            print(f"[AI Service] 从缓存获取五维图谱，用户: {user_id}")
            return cached_result
        
        # 优先使用resume_id，如果没有则使用user_id
        resume_text = self._get_resume_text(user_id, db, resume_id)
        
        # 如果没有简历数据，返回默认数据
        if resume_text == "暂无简历信息":
            return self._get_default_radar_data()
        
        # 使用AI分析各维度
        prompt = f"""请分析以下简历，为五个维度打分（0-100）并给出详细描述：

简历文本：
{resume_text}

请返回JSON格式：
{{
    "技能": {{"score": 85, "description": "精通Vue.js、React等前端框架，熟悉Node.js后端开发"}},
    "项目": {{"score": 75, "description": "参与过3个大型企业级项目开发，有丰富的项目经验"}},
    "履历": {{"score": 80, "description": "拥有3年前端开发经验，在知名互联网公司任职"}},
    "学业": {{"score": 90, "description": "北京大学计算机专业本科毕业，成绩优秀"}},
    "成果": {{"score": 70, "description": "获得AWS认证，参与开源项目贡献"}}
}}

要求：
1. 分数必须在0-100之间的整数
2. 描述要简洁明了，突出该维度的优势
3. 确保JSON格式正确，可以被解析"""
        
        response = self.qwen_client.chat(prompt)
        
        if response["success"]:
            parsed_result = self.qwen_client.parse_json_response(response["content"])
            if parsed_result:
                result = self._format_radar_result(parsed_result)
                # 保存到缓存
                self._set_cache(user_id, "ability_radar", result, db, resume_id)
                return result
        
        # 如果AI调用失败，返回默认数据
        return self._get_default_radar_data()
    
    def _format_radar_result(self, ai_result):
        """格式化雷达图结果"""
        dimensions = ["技能", "项目", "履历", "学业", "成果"]
        values = []
        dimension_details = {}
        
        for dim in dimensions:
            if dim in ai_result and isinstance(ai_result[dim], dict):
                values.append(ai_result[dim].get("score", 50))
                dimension_details[dim] = {
                    "score": ai_result[dim].get("score", 50),
                    "description": ai_result[dim].get("description", "暂无描述")
                }
            else:
                values.append(50)
                dimension_details[dim] = {"score": 50, "description": "暂无描述"}
        
        return {
            "dimensions": dimensions,
            "values": values,
            "details": dimension_details
        }
    
    def _get_default_radar_data(self):
        """获取默认雷达图数据（使用模拟数据展示）"""
        return {
            "dimensions": ["技能", "项目", "履历", "学业", "成果"],
            "values": [0, 0, 0, 0, 0],
            "details": {
                "技能": {"score": 0, "description": "请上传简历以获取分析"},
                "项目": {"score": 0, "description": "请上传简历以获取分析"},
                "履历": {"score": 0, "description": "请上传简历以获取分析"},
                "学业": {"score": 0, "description": "请上传简历以获取分析"},
                "成果": {"score": 0, "description": "请上传简历以获取分析"}
            }
        }
    
    def create_ability_map(self, user_id, ability_data, db):
        """创建能力图谱"""
        return {"message": "能力图谱创建成功", "data": ability_data}
    
    def update_ability_node(self, node_id, node_data, db):
        """更新能力节点"""
        return {"message": "能力节点更新成功", "data": node_data}
    
    def delete_ability_map(self, user_id, db):
        """删除能力图谱"""
        return {"message": "能力图谱删除成功"}
    
    def get_text_analysis(self, user_id, db, resume_id=None):
        """使用AI进行深度文本分析（适应所有行业）"""
        
        # 先尝试从缓存获取
        cached_result = self._get_cache(user_id, "text_analysis", db, resume_id)
        if cached_result:
            print(f"[AI Service] 从缓存获取文本分析，用户: {user_id}")
            return cached_result
        
        resume_text = self._get_resume_text(user_id, db, resume_id)
        
        # 如果没有简历数据，返回默认分析
        if resume_text == "暂无简历信息":
            return self._get_default_text_analysis()
        
        # 使用AI进行深度分析（简洁专业的提示词）
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
        
        if response["success"]:
            parsed_result = self.qwen_client.parse_json_response(response["content"])
            if parsed_result and "strengths" in parsed_result:
                result = self._format_text_analysis(parsed_result)
                # 保存到缓存
                self._set_cache(user_id, "text_analysis", result, db, resume_id)
                return result
        
        # 如果AI调用失败，返回默认分析
        return self._get_default_text_analysis()
    
    def _format_text_analysis(self, ai_result):
        """格式化文本分析结果（转换为前端期望的字符串格式）"""
        # 使用新的字段名 strengths/weaknesses
        strengths = ai_result.get("strengths", [])
        weaknesses = ai_result.get("weaknesses", [])
        suggestions = ai_result.get("suggestions", [])
        
        # 将数组转换为字符串（用"、"分隔）
        if isinstance(strengths, list):
            advantages_str = "、".join(strengths) + "。" if strengths else "暂无明显优势。"
        else:
            advantages_str = str(strengths) if strengths else "暂无明显优势。"
        
        if isinstance(weaknesses, list):
            disadvantages_str = "、".join(weaknesses) + "。" if weaknesses else "暂无明显劣势。"
        else:
            disadvantages_str = str(weaknesses) if weaknesses else "暂无明显劣势。"
        
        if isinstance(suggestions, list):
            # 去除每条建议末尾的句号，然后用"、"连接，最后加一个句号
            cleaned_suggestions = [s.rstrip('。').strip() for s in suggestions if s.strip()]
            suggestions_str = "、".join(cleaned_suggestions) if cleaned_suggestions else "建议继续保持和提升现有能力。"
        else:
            suggestions_str = str(suggestions).rstrip('。').strip() if suggestions else "建议继续保持和提升现有能力。"
        
        result = {
            "advantages": advantages_str,
            "disadvantages": disadvantages_str,
            "suggestions": suggestions_str,
            "dimensions": self._get_dimensions_from_analysis(ai_result)
        }
        
        # 添加行业和概览信息（如果有）
        if ai_result.get("industry"):
            result["industry"] = ai_result["industry"]
        if ai_result.get("overview"):
            result["overview"] = ai_result["overview"]
        
        return result
    
    def _get_dimensions_from_analysis(self, ai_result):
        """从分析结果中提取维度信息（用于前端展示）"""
        dimensions = ai_result.get("dimensions", {})
        
        return {
            "education": {
                "score": dimensions.get("education", {}).get("score", 0) or dimensions.get("education", {}).get("score", 0),
                "description": dimensions.get("education", {}).get("desc", "") or dimensions.get("education", {}).get("description", "请上传简历以获取分析")
            },
            "skills": {
                "score": dimensions.get("skills", {}).get("score", 0),
                "description": dimensions.get("skills", {}).get("desc", "") or dimensions.get("skills", {}).get("description", "请上传简历以获取分析")
            },
            "certificates": {
                "score": dimensions.get("certificates", {}).get("score", 0),
                "description": dimensions.get("certificates", {}).get("desc", "") or dimensions.get("certificates", {}).get("description", "请上传简历以获取分析")
            },
            "work_experience": {
                "score": dimensions.get("experience", {}).get("score", 0) or dimensions.get("work_experience", {}).get("score", 0),
                "description": dimensions.get("experience", {}).get("desc", "") or dimensions.get("work_experience", {}).get("description", "请上传简历以获取分析")
            },
            "project_experience": {
                "score": dimensions.get("projects", {}).get("score", 0) or dimensions.get("project_experience", {}).get("score", 0),
                "description": dimensions.get("projects", {}).get("desc", "") or dimensions.get("project_experience", {}).get("description", "请上传简历以获取分析")
            }
        }
    
    def _get_default_text_analysis(self):
        """获取默认文本分析数据（无数据时显示提示）"""
        return {
            "advantages": "请上传简历以获取真实分析",
            "disadvantages": "请上传简历以获取真实分析",
            "suggestions": "请上传简历以获取真实分析",
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
    
    def get_ability_universe(self, user_id, db, resume_id=None):
        """
        获取能力宇宙分析结果
        包含：能力宇宙总览、能力证据链、成长路径、贡献分析、文本报告
        """
        
        # 先尝试从缓存获取
        cached_result = self._get_cache(user_id, "ability_universe", db, resume_id)
        if cached_result:
            print(f"[AI Service] 从缓存获取能力宇宙，用户: {user_id}")
            return cached_result
        
        # 解析简历数据
        resume_data = self._parse_resume_data(user_id, db, resume_id)
        
        # 能力宇宙功能已移除，直接返回默认数据
        print(f"[AI Service] 能力宇宙功能已移除，返回默认数据")
        return self._get_default_ability_universe()
    
    def _parse_resume_data(self, user_id, db, resume_id=None):
        """
        解析简历数据为结构化格式
        优先从统一的 experiences 字段解析数据，按 type 分类
        """
        resume_text = self._get_resume_text(user_id, db, resume_id)
        
        # 从Resume表获取原始数据
        if resume_id:
            try:
                resume_id_int = int(resume_id)
                resumes = db.query(Resume).filter(Resume.id == resume_id_int).all()
            except (ValueError, TypeError):
                resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
        else:
            resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
        
        resume_data = {
            "name": "未知用户",
            "skills": [],
            "certificates": [],
            "projects": [],
            "work_experience": [],
            "internship_experience": [],
            "honors": [],
            "education": None
        }
        
        if resumes:
            resume = resumes[0]
            resume_data["name"] = resume.name or "未知用户"
            
            # 解析技能
            if resume.skills:
                try:
                    if isinstance(resume.skills, str):
                        import json
                        parsed_skills = json.loads(resume.skills)
                        if isinstance(parsed_skills, list):
                            resume_data["skills"] = parsed_skills
                        else:
                            resume_data["skills"] = [s.strip() for s in resume.skills.split(',') if s.strip()]
                    else:
                        resume_data["skills"] = resume.skills
                except:
                    resume_data["skills"] = [s.strip() for s in str(resume.skills).split(',') if s.strip()]
            
            # 解析证书
            if resume.certificates:
                try:
                    if isinstance(resume.certificates, str):
                        import json
                        parsed_certs = json.loads(resume.certificates)
                        if isinstance(parsed_certs, list):
                            resume_data["certificates"] = parsed_certs
                        else:
                            resume_data["certificates"] = [c.strip() for c in str(resume.certificates).split(',') if c.strip()]
                    else:
                        resume_data["certificates"] = resume.certificates
                except:
                    resume_data["certificates"] = [c.strip() for c in str(resume.certificates).split(',') if c.strip()]
            
            # ====== 优先从统一的 experiences 字段解析 ======
            experiences_parsed = []
            if getattr(resume, "experiences", None):
                try:
                    exp_data = getattr(resume, "experiences")
                    if isinstance(exp_data, str):
                        import json
                        experiences_parsed = json.loads(exp_data)
                    elif isinstance(exp_data, list):
                        experiences_parsed = exp_data
                except:
                    pass
            
            # 按 type 分类到不同数组
            for exp in experiences_parsed:
                if isinstance(exp, dict):
                    exp_type = exp.get('type', 'work')
                    exp_name = exp.get('name') or exp.get('company') or exp.get('position')
                    if not exp_name:
                        desc = exp.get('description', '')
                        exp_name = desc[:20] + '...' if len(desc) > 20 else desc
                    
                    if exp_type == 'project':
                        resume_data["projects"].append({"name": exp_name.strip() if exp_name else "项目"})
                    elif exp_type == 'internship':
                        resume_data["internship_experience"].append({"name": exp_name.strip() if exp_name else "实习经历"})
                    else:  # work 或其他
                        resume_data["work_experience"].append({"name": exp_name.strip() if exp_name else "工作经历"})
            
            # ====== 兼容旧数据：从独立字段读取（仅当 experiences 为空时） ======
            if not experiences_parsed:
                # 解析项目经历
                if resume.projects:
                    try:
                        if isinstance(resume.projects, str):
                            import json
                            parsed_projects = json.loads(resume.projects)
                            if isinstance(parsed_projects, list):
                                processed_projects = []
                                for proj in parsed_projects:
                                    if isinstance(proj, dict):
                                        proj_name = proj.get('name') or proj.get('company') or proj.get('position')
                                        if not proj_name:
                                            desc = proj.get('description', '')
                                            proj_name = desc[:20] + '...' if len(desc) > 20 else desc
                                        processed_projects.append({"name": proj_name.strip() if proj_name else "项目"})
                                    else:
                                        processed_projects.append({"name": str(proj).strip()})
                                resume_data["projects"] = processed_projects
                            else:
                                resume_data["projects"] = [{"name": p.strip()} for p in str(resume.projects).split(',') if p.strip()]
                        else:
                            resume_data["projects"] = resume.projects
                    except:
                        resume_data["projects"] = [{"name": p.strip()} for p in str(resume.projects).split(',') if p.strip()]
                
                # 解析工作经验
                if resume.work_experience:
                    try:
                        if isinstance(resume.work_experience, str):
                            import json
                            parsed_work = json.loads(resume.work_experience)
                            if isinstance(parsed_work, list):
                                processed_work = []
                                for exp in parsed_work:
                                    if isinstance(exp, dict):
                                        exp_name = exp.get('name') or exp.get('company') or exp.get('position')
                                        if not exp_name:
                                            desc = exp.get('description', '')
                                            exp_name = desc[:20] + '...' if len(desc) > 20 else desc
                                        processed_work.append({"name": exp_name.strip() if exp_name else "工作经历"})
                                    else:
                                        processed_work.append({"name": str(exp).strip()})
                                resume_data["work_experience"] = processed_work
                            else:
                                resume_data["work_experience"] = [{"name": str(resume.work_experience)}]
                        else:
                            resume_data["work_experience"] = resume.work_experience
                    except:
                        resume_data["work_experience"] = [{"name": str(resume.work_experience)}]
                
                # 解析实习经历
                if getattr(resume, "internship_experience", None):
                    try:
                        intern_data = getattr(resume, "internship_experience")
                        if isinstance(intern_data, str):
                            import json
                            parsed_intern = json.loads(intern_data)
                            if isinstance(parsed_intern, list):
                                processed_intern = []
                                for exp in parsed_intern:
                                    if isinstance(exp, dict):
                                        exp_name = exp.get('name') or exp.get('company') or exp.get('position')
                                        if not exp_name:
                                            desc = exp.get('description', '')
                                            exp_name = desc[:20] + '...' if len(desc) > 20 else desc
                                        processed_intern.append({"name": exp_name.strip() if exp_name else "实习经历"})
                                    else:
                                        processed_intern.append({"name": str(exp).strip()})
                                resume_data["internship_experience"] = processed_intern
                            elif isinstance(parsed_intern, dict):
                                exp_name = parsed_intern.get('name') or parsed_intern.get('company') or parsed_intern.get('position')
                                if not exp_name:
                                    desc = parsed_intern.get('description', '')
                                    exp_name = desc[:20] + '...' if len(desc) > 20 else desc
                                resume_data["internship_experience"] = [{"name": exp_name.strip() if exp_name else "实习经历"}]
                            else:
                                resume_data["internship_experience"] = [{"name": str(intern_data)[:30]}]
                        else:
                            resume_data["internship_experience"] = [{"name": str(intern_data)[:30]}]
                    except:
                        resume_data["internship_experience"] = [{"name": str(getattr(resume, "internship_experience"))[:30]}]
            
            # 解析荣誉奖项
            if getattr(resume, "honors", None):
                try:
                    honors_data = getattr(resume, "honors")
                    if isinstance(honors_data, str):
                        import json
                        parsed_honors = json.loads(honors_data)
                        if isinstance(parsed_honors, list):
                            resume_data["honors"] = [h for h in parsed_honors if h and str(h).strip()]
                        else:
                            resume_data["honors"] = [h.strip() for h in str(honors_data).split(',') if h.strip()]
                    elif isinstance(honors_data, list):
                        resume_data["honors"] = [h for h in honors_data if h and str(h).strip()]
                    else:
                        resume_data["honors"] = []
                except:
                    honors_str = str(getattr(resume, "honors"))
                    if honors_str.strip() and honors_str not in ('[]', '{}'):
                        resume_data["honors"] = [h.strip() for h in honors_str.split(',') if h.strip()]
                    else:
                        resume_data["honors"] = []
            
            # 教育背景
            if resume.education or resume.school or resume.major or resume.degree:
                resume_data["education"] = {
                    "school": resume.school,
                    "major": resume.major,
                    "degree": resume.degree
                }
        
        return resume_data
    
    def _get_default_ability_universe(self):
        """获取默认能力宇宙数据"""
        return {
            "universe": {
                "core": {
                    "name": "未知用户",
                    "total_score": 60
                },
                "planets": [
                    {"id": "knowledge", "name": "知识域", "score": 0, "size": 40, "color": "#409EFF", "position": {"x": 1, "y": 0}},
                    {"id": "practice", "name": "实践域", "score": 0, "size": 40, "color": "#67C23A", "position": {"x": 0, "y": 1}},
                    {"id": "qualification", "name": "资质域", "score": 0, "size": 40, "color": "#E6A23C", "position": {"x": -1, "y": 0}},
                    {"id": "achievement", "name": "成果域", "score": 0, "size": 40, "color": "#F56C6C", "position": {"x": 0, "y": -1}}
                ]
            },
            "evidence_chain": {},
            "growth_path": [],
            "ability_contribution": {},
            "text_report": {
                "strengths": [],
                "main_evidences": [],
                "weaknesses": [],
                "comprehensive_evaluation": "请上传简历以获取真实分析"
            }
        }