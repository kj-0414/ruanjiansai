import json
from utils.graph_generator import generate_ability_graph

class GraphAgent:
    def __init__(self):
        self.dimensions = ["专业技能", "项目经历", "学历背景", "证书资质", "软技能"]
    
    def generate_graph(self, match_result: dict) -> dict:
        resume_skills = []
        job_skills = []
        
        if match_result.get("match_strengths"):
            for strength in match_result["match_strengths"]:
                if "具备技能" in strength:
                    resume_skills.append(strength.replace("具备技能：", ""))
        
        if match_result.get("match_gaps"):
            for gap in match_result["match_gaps"]:
                if "缺少技能" in gap:
                    job_skills.append(gap.replace("缺少技能：", ""))
        
        graph_data = generate_ability_graph(resume_skills, job_skills)
        
        dimensions_data = []
        total_score = match_result.get("match_score", 0)
        
        dimensions_data.append({
            "dimension": "专业技能",
            "score": match_result.get("skill_score", 50),
            "items": resume_skills[:5],
            "color": "#5470c6"
        })
        
        dimensions_data.append({
            "dimension": "项目经历",
            "score": match_result.get("experience_score", 50),
            "items": [],
            "color": "#91cc75"
        })
        
        dimensions_data.append({
            "dimension": "学历背景",
            "score": match_result.get("education_score", 50),
            "items": [],
            "color": "#fac858"
        })
        
        dimensions_data.append({
            "dimension": "证书资质",
            "score": match_result.get("certificate_score", 50),
            "items": [],
            "color": "#ee6666"
        })
        
        dimensions_data.append({
            "dimension": "软技能",
            "score": min(100, total_score + 10),
            "items": [],
            "color": "#73c0de"
        })
        
        return {
            "type": "radar",
            "dimensions": dimensions_data,
            "match_score": total_score,
            "ability_graph": graph_data,
            "matched_skills": resume_skills,
            "missing_skills": job_skills,
            "suggestions": match_result.get("suggestions", [])
        }
    
    def analyze_ability_gaps(self, match_result: dict) -> dict:
        gaps = match_result.get("match_gaps", [])
        strengths = match_result.get("match_strengths", [])
        
        gap_analysis = []
        for gap in gaps:
            if "缺少技能" in gap:
                skill = gap.replace("缺少技能：", "")
                gap_analysis.append({
                    "type": "skill",
                    "name": skill,
                    "severity": "high",
                    "suggestion": f"建议学习{skill}技能"
                })
            elif "工作经验" in gap:
                gap_analysis.append({
                    "type": "experience",
                    "name": "工作经验",
                    "severity": "medium",
                    "suggestion": "建议积累更多相关工作经验"
                })
            elif "学历" in gap:
                gap_analysis.append({
                    "type": "education",
                    "name": "学历",
                    "severity": "low",
                    "suggestion": "学历未达到最优要求，但可通过其他优势弥补"
                })
        
        strength_analysis = []
        for strength in strengths:
            if "具备技能" in strength:
                skill = strength.replace("具备技能：", "")
                strength_analysis.append({
                    "type": "skill",
                    "name": skill,
                    "level": "strong"
                })
        
        return {
            "gaps": gap_analysis,
            "strengths": strength_analysis,
            "overall_assessment": self._generate_assessment(match_result.get("match_score", 0))
        }
    
    def _generate_assessment(self, score):
        if score >= 80:
            return {
                "level": "优秀",
                "description": "您的能力与岗位高度匹配，建议积极投递。",
                "color": "#52c41a"
            }
        elif score >= 60:
            return {
                "level": "良好",
                "description": "您的能力与岗位有较好匹配度，建议针对性提升短板。",
                "color": "#faad14"
            }
        elif score >= 40:
            return {
                "level": "一般",
                "description": "您的能力与岗位存在一定差距，建议系统提升相关技能。",
                "color": "#fa8c16"
            }
        else:
            return {
                "level": "较差",
                "description": "当前与岗位匹配度较低，建议先积累相关经验和技能。",
                "color": "#f5222d"
            }
    
    def generate_report(self, match_result: dict, resume_profile: dict, job_profile: dict) -> dict:
        graph_data = self.generate_graph(match_result)
        gap_analysis = self.analyze_ability_gaps(match_result)
        
        return {
            "candidate_name": resume_profile.get("name", "未提供"),
            "job_title": job_profile.get("job_title", "未提供"),
            "match_score": match_result.get("match_score", 0),
            "assessment": gap_analysis["overall_assessment"],
            "dimensions": graph_data["dimensions"],
            "strengths": gap_analysis["strengths"],
            "gaps": gap_analysis["gaps"],
            "suggestions": match_result.get("suggestions", []),
            "career_advice": match_result.get("career_advice", ""),
            "generated_at": self._get_current_time()
        }
    
    def _get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")