import json
import re
from datetime import datetime
from modules.match.match_repository import MatchRepository
from modules.match.schemas import MatchRequest
from modules.match.exceptions import ResumeNotFoundException, JobNotFoundException, MatchNotFoundException
from modules.resume.exceptions import AccessDeniedException
from modules.message.message_service import MessageService
from modules.agents.match_agent import MatchAgent
from modules.agents.graph_agent import GraphAgent
from utils.graph_generator import generate_ability_graph
from utils.semantic_matcher import semantic_matcher
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


# 全局Agent实例
_match_agent = MatchAgent()
_graph_agent = GraphAgent()


def extract_json_from_response(text: str) -> dict:
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end+1]
        else:
            json_str = text

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


class MatchService:
    def __init__(self):
        self.repository = None
        self._kb_service = None

    def _safe_parse_json(self, json_str, default=None):
        """安全解析JSON，失败时记录日志并返回默认值"""
        if not json_str:
            return default
        
        if isinstance(json_str, (list, dict)):
            return json_str
        
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.warning(f"JSON解析失败: {str(e)[:100]}, 原始数据: {str(json_str)[:50]}")
            return default

    def _assess_data_quality(self, resume, job):
        """评估简历和岗位数据的完整性"""
        quality_issues = []
        quality_warnings = []
        
        resume_skills = self._safe_parse_json(resume.skills, [])
        resume_certs = self._safe_parse_json(getattr(resume, 'certificates', '[]'), [])
        resume_projects = self._safe_parse_json(getattr(resume, 'projects', '[]'), [])
        resume_work_exp = self._safe_parse_json(getattr(resume, 'work_experience', '[]'), [])
        
        if not resume.name or resume.name == '未知':
            quality_issues.append("简历缺少姓名信息")
        
        if not resume_skills or len(resume_skills) == 0:
            quality_issues.append("简历缺少技能信息，匹配结果可能不准确")
        elif len(resume_skills) < 3:
            quality_warnings.append("简历技能信息较少，建议补充更多技能")
        
        if not resume_school and not resume.major:
            quality_warnings.append("简历缺少教育背景信息")
        
        job_skills = self._safe_parse_json(getattr(job, 'skills_requirement', job.skills), [])
        
        if not job_skills or len(job_skills) == 0:
            quality_issues.append("岗位缺少技能要求，匹配结果可能不准确")
        
        if not getattr(job, 'job_name', None):
            quality_warnings.append("岗位名称不完整")
        
        data_quality_score = 100
        if quality_issues:
            data_quality_score -= len(quality_issues) * 30
        if quality_warnings:
            data_quality_score -= len(quality_warnings) * 10
        
        return {
            "quality_score": max(0, data_quality_score),
            "has_issues": len(quality_issues) > 0,
            "has_warnings": len(quality_warnings) > 0,
            "issues": quality_issues,
            "warnings": quality_warnings
        }

    @property
    def kb_service(self):
        """延迟加载知识库服务"""
        if self._kb_service is None:
            try:
                from modules.knowledge_base import KnowledgeBaseService
                self._kb_service = KnowledgeBaseService()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to load knowledge base: {e}")
                return None
        return self._kb_service

    def _init_repository(self, db: Session):
        if not self.repository:
            self.repository = MatchRepository(db)
    
    def _build_resume_profile(self, resume):
        """将resume对象转换为MatchAgent需要的格式"""
        skills = self._safe_parse_json(resume.skills, [])
        skills_detail = self._safe_parse_json(getattr(resume, 'skills_detail', None), [])
        
        all_skills = list(set([s.get('skill_name', s) if isinstance(s, dict) else s for s in skills + skills_detail]))
        
        return {
            'name': resume.name or '未提供',
            'phone': resume.phone or '未提供',
            'email': resume.email or '未提供',
            'education': resume.education or resume.degree or '未提供',
            'experience_years': str(getattr(resume, 'work_years', 0)) + '年' if getattr(resume, 'work_years', 0) else '未提供',
            'skills': all_skills,
            'highlights': self._safe_parse_json(getattr(resume, 'certificates', '[]'), [])
        }
    
    def _build_job_profile(self, job):
        """将job对象转换为MatchAgent需要的格式"""
        skills_req = self._safe_parse_json(getattr(job, 'skills_requirement', None), None)
        if skills_req:
            skills = [s.get('skill_name', s) if isinstance(s, dict) else s for s in skills_req]
        else:
            skills = self._safe_parse_json(getattr(job, 'skills', None), [])
        
        return {
            'job_title': job.job_name or '未提供',
            'salary_range': job.salary or '未提供',
            'location': job.location or '未提供',
            'job_type': '全职',
            'required_skills': skills,
            'required_education': job.education_requirement or '不限',
            'education_level': getattr(job, 'education_level', None),
            'required_experience': str(job.experience_requirement) + '年' if job.experience_requirement else '未提供',
            'education_penalty_rules': getattr(job, 'education_penalty_rules', None),
            'highlights': []
        }
    
    def calculate_match_score(self, resume, job):
        try:
            # 尝试使用MatchAgent进行匹配
            resume_profile = self._build_resume_profile(resume)
            job_profile = self._build_job_profile(job)
            
            agent_result = _match_agent.calculate_match(resume_profile, job_profile)
            
            # 如果Agent成功返回结果，直接使用
            if agent_result and 'match_score' in agent_result:
                return agent_result
        except Exception as e:
            print(f"[MatchService] Agent匹配失败: {e}")
        
        # Fallback到原有逻辑
        try:
            structured_result = self._calculate_structured_match(resume, job)
            structured_score = structured_result['score']
            traditional_score = self._calculate_traditional_match_score(resume, job)
            base_score = structured_score * 0.7 + traditional_score * 0.3
            penalty_factor = self._calculate_education_penalty(resume, job)
            final_score = base_score * penalty_factor

            match_strengths = structured_result.get('strengths', [])
            match_gaps = structured_result.get('gaps', [])
            suggestions = structured_result.get('suggestions', [])

            if final_score >= 80:
                match_strengths.append('匹配度很高')
                career_advice = '恭喜！您与该岗位匹配度很高，建议积极投递。'
            elif final_score >= 60:
                match_strengths.append('匹配度较好')
                match_gaps.append('仍有提升空间')
                career_advice = '您与该岗位有较好的匹配度，但仍有提升空间。'
            elif final_score >= 40:
                match_gaps.append('匹配度一般')
                career_advice = '您与该岗位存在一定差距，建议针对性提升。'
            else:
                match_gaps.append('匹配度较低')
                career_advice = '当前与该岗位匹配度较低，建议先积累相关经验。'

            if penalty_factor < 1.0:
                suggestions.append('学历未达到最优要求，可能影响匹配结果')
            
            data_quality = self._assess_data_quality(resume, job)
            
            if data_quality['has_issues']:
                for issue in data_quality['issues']:
                    suggestions.append(issue)
            
            return {
                'match_score': final_score,
                'structured_score': structured_score,
                'traditional_score': traditional_score,
                'education_penalty_factor': penalty_factor,
                'match_strengths': match_strengths,
                'match_gaps': match_gaps,
                'suggestions': suggestions,
                'interview_tips': ['准备详细的项目案例，突出核心技能的实际应用', '了解公司业务和技术栈'],
                'career_advice': career_advice,
                'weights': {
                    '结构化匹配': 0.7,
                    '传统匹配': 0.3
                },
                'data_quality': data_quality
            }
        except Exception as e:
            logger.error(f"匹配计算失败: {str(e)}")
            return {
                'match_score': self._calculate_traditional_match_score(resume, job),
                'match_strengths': [],
                'match_gaps': [],
                'suggestions': [],
                'career_advice': '匹配分析失败，请稍后重试',
                'interview_tips': [],
                'data_quality': self._assess_data_quality(resume, job)
            }

    def _calculate_structured_match(self, resume, job):
        strengths = []
        gaps = []
        suggestions = []

        resume_skills_detail = self._safe_getattr(resume, 'skills_detail', None)
        resume_certs = self._safe_getattr(resume, 'certificates', None)
        resume_projects = self._safe_getattr(resume, 'projects', None)
        resume_work_exp = self._safe_getattr(resume, 'work_experience', None)
        resume_work_years = self._safe_getattr(resume, 'work_years', None)

        job_skills_req = self._safe_getattr(job, 'skills_requirement', None)
        job_certs_req = self._safe_getattr(job, 'certificate_requirements', None)
        job_project_req = self._safe_getattr(job, 'project_requirements', None)
        job_min_exp = self._safe_getattr(job, 'min_experience_years', None)
        job_max_exp = self._safe_getattr(job, 'max_experience_years', None)

        resume_skills = self._parse_json_field(resume_skills_detail) or self._parse_json_field(resume.skills) or []
        resume_certs_list = self._parse_json_field(resume_certs) or []
        resume_projects_list = self._parse_json_field(resume_projects) or []
        resume_work_exp_list = self._parse_json_field(resume_work_exp) or []
        resume_work_years_val = resume_work_years or self._calculate_work_years(resume_work_exp_list)

        job_skills_req_list = self._parse_json_field(job_skills_req) or self._parse_json_field(job.skills) or []
        job_certs_req_list = self._parse_json_field(job_certs_req) or []
        job_project_req_list = self._parse_json_field(job_project_req) or []

        skill_score, skill_strengths, skill_gaps = self._calculate_skill_match(resume_skills, job_skills_req_list)
        strengths.extend(skill_strengths)
        gaps.extend(skill_gaps)

        cert_score, cert_strengths, cert_gaps = self._calculate_certificate_match(resume_certs_list, job_certs_req_list)
        strengths.extend(cert_strengths)
        gaps.extend(cert_gaps)

        exp_score, exp_strengths, exp_gaps = self._calculate_experience_match(resume_work_years_val, job, job_min_exp, job_max_exp)
        strengths.extend(exp_strengths)
        gaps.extend(exp_gaps)

        project_score, project_strengths, project_gaps = self._calculate_project_match(resume_projects_list, job_project_req_list)
        strengths.extend(project_strengths)
        gaps.extend(project_gaps)

        total_score = skill_score * 0.3 + cert_score * 0.2 + exp_score * 0.2 + project_score * 0.3

        return {
            'score': total_score,
            'strengths': list(set(strengths)),
            'gaps': list(set(gaps)),
            'suggestions': suggestions
        }

    def _parse_json_field(self, field):
        if not field:
            return None
        try:
            return json.loads(field)
        except:
            return None

    def _safe_getattr(self, obj, attr, default=None):
        try:
            return getattr(obj, attr, default)
        except:
            return default

    def _calculate_work_years(self, work_exp_list):
        if not work_exp_list:
            return 0
        total_years = 0
        for exp in work_exp_list:
            try:
                start_date = exp.get('start_date', '')
                if start_date:
                    total_years += 1
            except:
                pass
        return total_years

    def _calculate_skill_match(self, resume_skills, job_skills_req):
        strengths = []
        gaps = []

        if not job_skills_req:
            return 100, strengths, gaps

        if not resume_skills:
            gaps.append('缺少技能信息')
            return 0, strengths, gaps

        required_skills = [s for s in job_skills_req if s.get('required')]
        optional_skills = [s for s in job_skills_req if not s.get('required')]

        required_score = 0
        if required_skills:
            matched_required = 0
            for req_skill in required_skills:
                skill_name = req_skill.get('skill_name', '')
                matched, _ = self._find_matching_skill(skill_name, resume_skills)
                if matched:
                    matched_required += 1
                    strengths.append(f'具备必需技能：{skill_name}')
            required_score = (matched_required / len(required_skills)) * 100
            if matched_required < len(required_skills):
                gaps.append(f'缺少{len(required_skills) - matched_required}项必需技能')

        optional_score = 0
        if optional_skills:
            matched_optional = 0
            for opt_skill in optional_skills:
                skill_name = opt_skill.get('skill_name', '')
                matched, _ = self._find_matching_skill(skill_name, resume_skills)
                if matched:
                    matched_optional += 1
                    strengths.append(f'具备加分技能：{skill_name}')
            optional_score = (matched_optional / len(optional_skills)) * 100

        total_score = required_score * 0.7 + optional_score * 0.3
        return total_score, strengths, gaps

    def _find_matching_skill(self, job_skill, resume_skills, required_level='初级'):
        for resume_skill in resume_skills:
            skill_name = resume_skill.get('skill_name', '') or resume_skill if isinstance(resume_skill, str) else ''
            resume_level = resume_skill.get('level', 3)
            matched, score = semantic_matcher.match_skill(job_skill, [skill_name])
            if matched:
                level_factor = min(resume_level / 3, 1.5)
                return True, score * level_factor
        return False, 0

    def _enhance_skill_match_with_knowledge(self, resume_skills, job_skills):
        """
        使用知识库增强技能匹配
        返回增强后的匹配分数和建议
        """
        if not self.kb_service:
            return None

        try:
            resume_skill_names = [
                s.get('skill_name', '') if isinstance(s, dict) else str(s)
                for s in resume_skills
            ]
            job_skill_names = [
                s.get('skill_name', '') if isinstance(s, dict) else str(s)
                for s in job_skills
            ]

            match_result = self.kb_service.enhance_match(resume_skill_names, job_skill_names)

            if match_result and match_result.get('enhanced_score', 0) > 0:
                return {
                    'direct_score': match_result.get('direct_score', 0),
                    'related_score': match_result.get('related_score', 0),
                    'enhanced_score': match_result.get('enhanced_score', 0),
                    'direct_matches': match_result.get('direct_matches', []),
                    'related_matches': match_result.get('related_matches', []),
                    'missing_skills': match_result.get('missing_skills', []),
                    'skill_recommendations': self._get_skill_recommendations(
                        match_result.get('missing_skills', [])
                    )
                }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Knowledge base matching failed: {e}")

        return None

    def _get_skill_recommendations(self, missing_skills):
        """获取缺失技能的推荐学习技能"""
        if not self.kb_service or not missing_skills:
            return []

        recommendations = []
        for skill_name in missing_skills[:5]:
            recs = self.kb_service.get_skill_recommendations(skill_name, limit=3)
            for rec in recs:
                recommendations.append({
                    'skill': skill_name,
                    'recommended_skill': rec.get('skill_name'),
                    'reason': rec.get('suggestion', '')
                })

        return recommendations[:10]

    def _calculate_certificate_match(self, resume_certs, job_certs_req):
        strengths = []
        gaps = []

        if not job_certs_req:
            return 100, strengths, gaps

        if not resume_certs:
            gaps.append('缺少证书信息')
            return 0, strengths, gaps

        cert_names = [cert.get('name', '') for cert in resume_certs]
        required_certs = [req for req in job_certs_req if req.get('required')]

        if required_certs:
            matched_count = 0
            for req in required_certs:
                cert_name = req.get('name', '')
                matched, _ = semantic_matcher.match_certificate(cert_name, cert_names)
                if matched:
                    matched_count += 1
                    strengths.append(f'具备必需证书：{cert_name}')
            score = (matched_count / len(required_certs)) * 100
            if matched_count < len(required_certs):
                gaps.append(f'缺少{len(required_certs) - matched_count}项必需证书')
        else:
            score = 100

        return score, strengths, gaps

    def _calculate_experience_match(self, resume_work_years, job, min_years=None, max_years=None):
        strengths = []
        gaps = []

        job_min_years = min_years if min_years is not None else self._safe_getattr(job, 'min_experience_years', 0)
        job_max_years = max_years if max_years is not None else self._safe_getattr(job, 'max_experience_years', float('inf'))

        if resume_work_years >= job_min_years:
            strengths.append(f'工作经验符合要求（{resume_work_years}年）')
            if resume_work_years <= job_max_years:
                score = 100
            else:
                score = 80
                gaps.append('工作年限超出岗位要求范围')
        else:
            gaps.append(f'工作经验不足（需{job_min_years}年，当前{resume_work_years}年）')
            score = min((resume_work_years / job_min_years) * 100, 50) if job_min_years > 0 else 50

        return score, strengths, gaps

    def _calculate_project_match(self, resume_projects, job_project_req):
        strengths = []
        gaps = []

        if not job_project_req:
            return 100, strengths, gaps

        if not resume_projects:
            gaps.append('缺少项目经验信息')
            return 0, strengths, gaps

        matched_count = 0
        for req in job_project_req:
            domain = req.get('domain', '')
            tech_stack = req.get('tech_stack', [])

            for project in resume_projects:
                project_domain = project.get('domain', '')
                project_tech = project.get('tech_stack', [])

                domain_matched = semantic_matcher.calculate_similarity(domain, project_domain) >= 0.5

                tech_matched = False
                if tech_stack:
                    for tech in tech_stack:
                        matched, _ = semantic_matcher.match_skill(tech, project_tech)
                        if matched:
                            tech_matched = True
                            break
                else:
                    tech_matched = True

                if domain_matched and tech_matched:
                    matched_count += 1
                    strengths.append(f'项目经验匹配：{project.get("name", "")}')
                    break

        score = (matched_count / len(job_project_req)) * 100
        if matched_count < len(job_project_req):
            gaps.append(f'缺少{len(job_project_req) - matched_count}项项目经验要求')

        return score, strengths, gaps

    def _calculate_education_penalty(self, resume, job):
        edu_levels = {'高中': 1, '大专': 2, '本科': 3, '硕士': 4, '博士': 5}

        resume_level = edu_levels.get(resume.degree, 0) or edu_levels.get(resume.education, 0)
        job_level = edu_levels.get(self._safe_getattr(job, 'education_level', ''), 0) or edu_levels.get(job.education_requirement, 0)

        if job_level == 0 or resume_level >= job_level:
            return 1.0

        penalty = (job_level - resume_level) * 0.1
        return max(1.0 - penalty, 0.5)

    def _calculate_traditional_match_score(self, resume, job):
        location_score = self._calculate_location_match(resume, job)
        salary_score = self._calculate_salary_match(job)
        return location_score * 0.5 + salary_score * 0.5

    def _calculate_location_match(self, resume, job):
        resume_address = getattr(resume, 'address', '')
        job_location = job.location

        if not job_location:
            return 100

        if not resume_address:
            return 60

        def extract_city(location_str):
            cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '苏州',
                      '重庆', '天津', '青岛', '郑州', '长沙', '沈阳', '宁波', '济南', '无锡', '合肥']
            for city in cities:
                if city in location_str:
                    return city
            return location_str[:2]

        resume_city = extract_city(resume_address)
        job_city = extract_city(job_location)

        return 100 if resume_city == job_city else 50

    def _calculate_salary_match(self, job):
        salary = job.salary

        def extract_salary_value(salary_str):
            if not salary_str:
                return 0
            match = re.search(r'(\d+)[-~以上]?\s*[Kk]?', salary_str)
            if match:
                return int(match.group(1))
            return 0

        salary_value = extract_salary_value(salary)

        if salary_value >= 50:
            return 100
        elif salary_value >= 40:
            return 90
        elif salary_value >= 30:
            return 80
        elif salary_value >= 20:
            return 70
        elif salary_value >= 10:
            return 60
        else:
            return 50

    def create_ability_tree(self, user_id, db):
        return {
            "name": f"User_{user_id}",
            "children": [
                {"name": "专业技能", "children": [{"name": "Python"}, {"name": "Java"}], "weight": 0.4},
                {"name": "工作经验", "children": [], "weight": 0.3},
                {"name": "学历要求", "children": [], "weight": 0.15},
                {"name": "证书资质", "children": [], "weight": 0.15}
            ]
        }

    def create_job_requirement_tree(self, job_id, db):
        return {
            "name": f"Job_{job_id}",
            "children": [
                {"name": "专业技能", "children": [{"name": "Python"}, {"name": "SQL"}], "weight": 0.4},
                {"name": "工作经验", "children": [], "weight": 0.3},
                {"name": "学历要求", "children": [], "weight": 0.15},
                {"name": "证书资质", "children": [], "weight": 0.15}
            ]
        }

    def calculate_match_score(self, ability_tree, requirement_tree):
        return 75.0

    def get_match_details(self, ability_tree, requirement_tree):
        return [{"name": "Python"}, {"name": "SQL"}], [{"name": "Java"}]

    def match_resume_job(self, request: MatchRequest, db: Session) -> dict:
        self._init_repository(db)

        resume = self.repository.get_resume(request.resume_id)
        if not resume:
            raise ResumeNotFoundException("Resume not found")

        job = self.repository.get_job(request.job_id)
        if not job:
            raise JobNotFoundException("Job not found")

        ability_tree = self.create_ability_tree(resume.user_id, db)
        requirement_tree = self.create_job_requirement_tree(request.job_id, db)
        match_score = self.calculate_match_score(ability_tree, requirement_tree)
        matched_nodes, missing_nodes = self.get_match_details(ability_tree, requirement_tree)

        match_strengths = [f"{node['name']}" for node in matched_nodes[:10]]
        match_gaps = [f"{node['name']}" for node in missing_nodes[:10]]
        suggestions = []
        interview_tips = ['准备详细的项目案例，突出核心技能的实际应用', '了解公司业务和技术栈']

        if match_score >= 80:
            match_strengths.insert(0, '匹配度很高')
            career_advice = '恭喜！您与该岗位匹配度很高，建议积极投递。'
        elif match_score >= 60:
            match_strengths.insert(0, '匹配度较好')
            match_gaps.insert(0, '仍有提升空间')
            career_advice = '您与该岗位有较好的匹配度，但仍有提升空间。'
        elif match_score >= 40:
            match_gaps.insert(0, '匹配度一般')
            career_advice = '您与该岗位存在一定差距，建议针对性提升。'
        else:
            match_gaps.insert(0, '匹配度较低')
            career_advice = '当前与该岗位匹配度较低，建议先积累相关经验。'

        resume_skills = set(json.loads(resume.skills) if resume.skills else [])
        job_skills = set()
        job_desc_lower = job.job_desc.lower()
        skill_keywords = [
            'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'go', 'rust', 'php', 'ruby',
            'html', 'css', 'react', 'vue', 'angular', 'node.js', 'django', 'flask', 'spring',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server',
            'linux', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', '阿里云', '腾讯云',
            'git', 'jenkins', 'ci/cd', 'nginx', 'apache', 'tomcat',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
            'nlp', 'computer vision', 'data analysis', 'big data', 'hadoop', 'spark',
            'android', 'ios', 'flutter', 'react native', 'wechat mini program',
            'photoshop', 'illustrator', 'figma', 'sketch', 'axure',
            '项目管理', '团队协作', '沟通能力', '问题解决'
        ]
        for skill in skill_keywords:
            if skill.lower() in job_desc_lower:
                job_skills.add(skill)

        ability_graph = generate_ability_graph(resume_skills, job_skills)

        match_data = {
            "resume_id": request.resume_id,
            "job_id": request.job_id,
            "match_score": match_score,
            "match_tags": json.dumps(match_strengths),
            "gap_tags": json.dumps(match_gaps),
            "ability_graph": json.dumps(ability_graph)
        }

        new_match = self.repository.create_match(match_data)

        return {
            "id": new_match.id,
            "resume_id": new_match.resume_id,
            "job_id": new_match.job_id,
            "match_score": new_match.match_score,
            "match_tags": json.loads(new_match.match_tags) if new_match.match_tags else [],
            "gap_tags": json.loads(new_match.gap_tags) if new_match.gap_tags else [],
            "match_strengths": match_strengths,
            "match_gaps": match_gaps,
            "ability_graph": json.loads(new_match.ability_graph) if new_match.ability_graph else {},
            "suggestions": suggestions,
            "interview_tips": interview_tips,
            "career_advice": career_advice,
            "create_time": new_match.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_match_records(self, db: Session) -> list:
        self._init_repository(db)
        matches = self.repository.get_all_matches()
        result = []
        for match in matches:
            result.append({
                "id": match.id,
                "resume_id": match.resume_id,
                "job_id": match.job_id,
                "match_score": match.match_score,
                "match_tags": json.loads(match.match_tags) if match.match_tags else [],
                "gap_tags": json.loads(match.gap_tags) if match.gap_tags else [],
                "ability_graph": json.loads(match.ability_graph) if match.ability_graph else {},
                "create_time": match.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return result

    def get_recommendations(self, user_id: str, user_role: str, db: Session) -> list:
        self._init_repository(db)
        recommendations = []

        if user_role == "job_seeker":
            resumes = self.repository.get_resumes_by_user(user_id)
            resume_ids = [resume.id for resume in resumes]

            if resume_ids:
                matches = self.repository.get_all_matches()
                resume_matches = [m for m in matches if m.resume_id in resume_ids][:5]

                for match in resume_matches:
                    job = self.repository.get_job(match.job_id)
                    if job:
                        recommendations.append({
                            "type": "job",
                            "id": job.id,
                            "name": job.job_name,
                            "salary": job.salary,
                            "match_score": match.match_score,
                            "match_tags": json.loads(match.match_tags) if match.match_tags else [],
                            "gap_tags": json.loads(match.gap_tags) if match.gap_tags else []
                        })

        elif user_role == "company":
            jobs = self.repository.get_jobs_by_user(user_id)
            job_ids = [job.id for job in jobs]

            if job_ids:
                matches = self.repository.get_all_matches()
                job_matches = [m for m in matches if m.job_id in job_ids][:5]

                for match in job_matches:
                    resume = self.repository.get_resume(match.resume_id)
                    if resume:
                        recommendations.append({
                            "type": "resume",
                            "id": resume.id,
                            "name": resume.resume_name,
                            "match_score": match.match_score,
                            "match_tags": json.loads(match.match_tags) if match.match_tags else [],
                            "gap_tags": json.loads(match.gap_tags) if match.gap_tags else []
                        })

        return recommendations

    def get_match_record(self, match_id: int, db: Session) -> dict:
        self._init_repository(db)
        match = self.repository.get_match_by_id(match_id)
        if not match:
            raise MatchNotFoundException("Match record not found")

        return {
            "id": match.id,
            "resume_id": match.resume_id,
            "job_id": match.job_id,
            "match_score": match.match_score,
            "match_tags": json.loads(match.match_tags) if match.match_tags else [],
            "gap_tags": json.loads(match.gap_tags) if match.gap_tags else [],
            "ability_graph": json.loads(match.ability_graph) if match.ability_graph else {},
            "create_time": match.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def deliver_resume(self, resume_id: int, job_id: int, user_id: str, db: Session) -> dict:
        self._init_repository(db)
        
        resume = self.repository.get_resume(resume_id)
        if not resume:
            raise ResumeNotFoundException("Resume not found")
        
        job = self.repository.get_job(job_id)
        if not job:
            raise JobNotFoundException("Job not found")
        
        if resume.user_id != user_id:
            raise AccessDeniedException("You can only deliver your own resume")
        
        existing_delivery = self.repository.get_delivery(resume_id, job_id)
        if existing_delivery:
            return {
                "success": False,
                "message": "简历已投递过该岗位"
            }
        
        delivery_data = {
            "resume_id": resume_id,
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        new_delivery = self.repository.create_delivery(delivery_data)
        
        message_service = MessageService()
        conversation = message_service.create_conversation(
            db=db,
            job_seeker_id=resume.user_id,
            company_id=job.user_id,
            job_id=job_id,
            resume_id=resume_id
        )
        
        return {
            "success": True,
            "message": "投递成功，请等待企业开启会话",
            "delivery_id": new_delivery.id,
            "conversation_id": conversation.id,
            "create_time": new_delivery.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }