import json
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from modules.knowledge_base.db import KnowledgeBaseDB
from utils.semantic_matcher import semantic_matcher
from modules.agents.weight_learner import WeightLearner, WeightConfig

class MatchAgent:
    weights: Dict[str, float]
    
    def __init__(self, use_data_driven_weights: bool = True) -> None:
        self.knowledge_base: KnowledgeBaseDB = KnowledgeBaseDB()
        self.weight_learner: WeightLearner = WeightLearner()
        self.use_data_driven_weights: bool = use_data_driven_weights
        
        self._load_weights()

    def _load_weights(self, industry: Optional[str] = None) -> None:
        """加载权重配置"""
        if self.use_data_driven_weights:
            config: WeightConfig = self.weight_learner.get_weights(industry)
            self.weights = config.to_dict()
        else:
            self.weights = {
                "skills": 0.4,
                "experience": 0.25,
                "education": 0.15,
                "certificates": 0.1,
                "location": 0.1
            }

    def calculate_match(self, 
                        resume_profile: Dict[str, Any], 
                        job_profile: Dict[str, Any], 
                        db=None, 
                        industry: Optional[str] = None) -> Dict[str, Any]:
        # 加载行业特定权重
        if industry:
            self._load_weights(industry)
        
        resume_skills = set(resume_profile.get("skills", []))
        job_skills = set(job_profile.get("required_skills", []))
        
        skill_score, skill_matched, skill_missing = self._calculate_skill_match(resume_skills, job_skills, db)
        experience_score = self._calculate_experience_match(resume_profile, job_profile)
        education_score = self._calculate_education_match(resume_profile, job_profile)
        certificate_score = self._calculate_certificate_match(resume_profile, job_profile)
        location_score = self._calculate_location_match(resume_profile, job_profile)
        
        total_score = (
            skill_score * self.weights["skills"] +
            experience_score * self.weights["experience"] +
            education_score * self.weights["education"] +
            certificate_score * self.weights["certificates"] +
            location_score * self.weights["location"]
        )
        
        # 应用学历惩罚
        education_penalty_factor = 1.0
        education_penalty_applied = False
        education_penalty_rules = job_profile.get("education_penalty_rules")
        if education_penalty_rules:
            penalty_result = self._apply_education_penalty(
                total_score,
                resume_profile,
                job_profile,
                education_penalty_rules
            )
            total_score = penalty_result["final_score"]
            education_penalty_factor = penalty_result["penalty_factor"]
            education_penalty_applied = penalty_result["applied"]
        
        match_strengths = []
        match_gaps = []
        suggestions = []
        
        if skill_matched:
            skill_matched_list = list(skill_matched)
            match_strengths.extend([f"具备技能：{s}" for s in skill_matched_list[:3]])
        if skill_missing:
            skill_missing_list = list(skill_missing)
            match_gaps.extend([f"缺少技能：{s}" for s in skill_missing_list[:3]])
        
        if experience_score >= 80:
            match_strengths.append("工作经验符合要求")
        elif experience_score >= 60:
            match_gaps.append("工作经验略低于要求")
        else:
            match_gaps.append("工作经验不足")
        
        if education_score >= 80:
            match_strengths.append("学历符合要求")
        else:
            match_gaps.append("学历未达到最优要求")
        
        if education_penalty_applied:
            suggestions.append(f"学历未达到岗位要求，匹配分数已按岗位设置进行调整（惩罚因子：{education_penalty_factor}）")
        
        if total_score >= 80:
            match_strengths.insert(0, '匹配度很高')
            career_advice = '恭喜！您与该岗位匹配度很高，建议积极投递。'
        elif total_score >= 60:
            match_strengths.insert(0, '匹配度较好')
            match_gaps.insert(0, '仍有提升空间')
            career_advice = '您与该岗位有较好的匹配度，但仍有提升空间。'
        elif total_score >= 40:
            match_gaps.insert(0, '匹配度一般')
            career_advice = '您与该岗位存在一定差距，建议针对性提升。'
        else:
            match_gaps.insert(0, '匹配度较低')
            career_advice = '当前与该岗位匹配度较低，建议先积累相关经验。'
        
        for missing_skill in list(skill_missing)[:2]:
            suggestions.append(f"建议学习{missing_skill}技能，提升与岗位的匹配度。")
        
        return {
            "match_score": round(total_score, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "certificate_score": round(certificate_score, 2),
            "location_score": round(location_score, 2),
            "education_penalty_factor": education_penalty_factor,
            "education_penalty_applied": education_penalty_applied,
            "match_strengths": match_strengths,
            "match_gaps": match_gaps,
            "suggestions": suggestions,
            "interview_tips": [
                '准备详细的项目案例，突出核心技能的实际应用',
                '了解公司业务和技术栈'
            ],
            "career_advice": career_advice,
            "weights": self.weights,
            "matched_skills": list(skill_matched),
            "missing_skills": list(skill_missing)
        }

    def _calculate_skill_match(self, resume_skills: Set[str], job_skills: Set[str], db=None) -> Tuple[float, Set[str], Set[str]]:
        if not job_skills:
            return 100.0, set(), set()
        
        if not resume_skills:
            return 0.0, set(), set(job_skills)
        
        matched = set()
        missing = set()
        weighted_score = 0.0
        total_weight = 0.0
        
        for job_skill in job_skills:
            found = False
            skill_weight = 1.0  # 默认权重
            
            # 获取技能的需求权重（从知识库）
            skill_info = self.knowledge_base.get_skill_info(job_skill)
            if skill_info and 'demand_weight' in skill_info:
                # 使用需求权重的对数（避免极端值）
                demand_weight = skill_info['demand_weight']
                if demand_weight > 0:
                    # 需求权重映射到 0.5-2.0 范围
                    skill_weight = 0.5 + min(demand_weight * 50, 1.5)
            
            normalized_job = self._normalize_skill(job_skill)
            if normalized_job in [self._normalize_skill(s) for s in resume_skills]:
                matched.add(job_skill)
                found = True
            else:
                for resume_skill in resume_skills:
                    if semantic_matcher.match_skill(job_skill, [resume_skill]):
                        matched.add(job_skill)
                        found = True
                        break
            
            if not found:
                related_skills = self._get_related_skills(job_skill, db)
                if related_skills:
                    for related in related_skills:
                        if related in resume_skills:
                            matched.add(job_skill)
                            found = True
                            break
            
            if not found:
                missing.add(job_skill)
            
            # 使用加权分数计算
            if found:
                weighted_score += skill_weight
            total_weight += skill_weight
        
        # 加权平均分数
        score = (weighted_score / total_weight * 100) if total_weight > 0 else 0
        return score, matched, missing

    def _normalize_skill(self, skill: str) -> str:
        return skill.lower().strip().replace(" ", "")

    def _get_related_skills(self, skill: str, db=None) -> List[str]:
        try:
            if db:
                relations = self.knowledge_base.get_skill_relations(skill_name=skill, db=db)
            else:
                relations = self.knowledge_base.get_skill_relations(skill_name=skill)
            
            related: List[str] = []
            for rel in relations:
                if rel.get("relation_type") in ["related_to", "belongs_to", "requires"]:
                    related.append(rel.get("target_skill", ""))
            
            return [r for r in related if r]
        except Exception:
            return []

    def get_skill_gap_analysis(self, resume_skills: List[str], job_skills: List[str], db=None) -> Dict[str, Any]:
        resume_skill_set = set(resume_skills)
        job_skill_set = set(job_skills)
        
        missing_skills = job_skill_set - resume_skill_set
        matched_skills = job_skill_set & resume_skill_set
        
        skill_gap_details = []
        for missing in missing_skills:
            gap_info = {
                "skill": missing,
                "learning_resources": [],
                "related_skills": [],
                "difficulty": "unknown",
                "estimated_time": "unknown"
            }
            
            try:
                if db:
                    kb_skill = self.knowledge_base.get_skill_by_name(missing, db=db)
                else:
                    kb_skill = self.knowledge_base.get_skill_by_name(missing)
                
                if kb_skill:
                    gap_info["category"] = kb_skill.get("category", "")
                    gap_info["difficulty"] = kb_skill.get("difficulty", "unknown")
                    gap_info["description"] = kb_skill.get("description", "")
                    
                    if db:
                        relations = self.knowledge_base.get_skill_relations(skill_name=missing, db=db)
                    else:
                        relations = self.knowledge_base.get_skill_relations(skill_name=missing)
                    
                    prereqs = [r["target_skill"] for r in relations if r.get("relation_type") == "requires"]
                    related = [r["target_skill"] for r in relations if r.get("relation_type") in ["related_to", "belongs_to"]]
                    
                    gap_info["prerequisites"] = prereqs
                    gap_info["related_skills"] = related
                    
                    gap_info["learning_resources"] = self._generate_learning_suggestions(missing, related, kb_skill.get("category", ""))
            except Exception as e:
                print(f"[MatchAgent] Skill gap analysis error for {missing}: {e}")
            
            skill_gap_details.append(gap_info)
        
        skill_gap_details.sort(key=lambda x: (
            0 if x.get("difficulty") == "easy" else
            1 if x.get("difficulty") == "medium" else
            2 if x.get("difficulty") == "hard" else 3
        ))
        
        return {
            "total_required": len(job_skills),
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills),
            "match_rate": round(len(matched_skills) / len(job_skills) * 100, 2) if job_skills else 100,
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "skill_gap_details": skill_gap_details,
            "learning_priority": [g["skill"] for g in skill_gap_details[:3]]
        }

    def _generate_learning_suggestions(self, skill: str, related_skills: List[str], category: str) -> List[Dict[str, str]]:
        suggestions = []
        
        suggestions.append({
            "type": "core",
            "skill": skill,
            "suggestion": f"深入学习{skill}核心概念和基础用法",
            "priority": "high"
        })
        
        for related in related_skills[:2]:
            suggestions.append({
                "type": "related",
                "skill": related,
                "suggestion": f"了解{related}，它与{skill}经常一起使用",
                "priority": "medium"
            })
        
        if category:
            suggestions.append({
                "type": "category",
                "skill": category,
                "suggestion": f"关注{category}领域的发展趋势",
                "priority": "low"
            })
        
        return suggestions

    def enhance_match(self, 
                    match_result: Dict[str, Any], 
                    resume_profile: Dict[str, Any], 
                    job_profile: Dict[str, Any], 
                    db=None) -> Dict[str, Any]:
        enhanced: Dict[str, Any] = match_result.copy()
        
        skill_gap = self.get_skill_gap_analysis(
            resume_profile.get("skills", []),
            job_profile.get("required_skills", []),
            db
        )
        enhanced["skill_gap_analysis"] = skill_gap
        
        if skill_gap.get("missing_skills"):
            enhanced["learning_roadmap"] = self._generate_learning_roadmap(
                skill_gap["skill_gap_details"],
                resume_profile.get("skills", [])
            )
        
        enhanced["interview_preparation"] = self._generate_interview_prep(
            matched_skills=skill_gap.get("matched_skills", []),
            missing_skills=skill_gap.get("missing_skills", []),
            job_profile=job_profile
        )
        
        enhanced["career_progression"] = self._analyze_career_progression(
            current_skills=resume_profile.get("skills", []),
            target_skills=job_profile.get("required_skills", []),
            db=db
        )
        
        return enhanced

    def _generate_learning_roadmap(self, 
                                   skill_gaps: List[Dict[str, Any]], 
                                   current_skills: List[str]) -> List[Dict[str, Any]]:
        roadmap: List[Dict[str, Any]] = []
        current_skill_set: Set[str] = set(current_skills)
        
        for i, gap in enumerate(skill_gaps[:5]):
            stage: Dict[str, Any] = {
                "stage": i + 1,
                "skill": gap["skill"],
                "duration": gap.get("estimated_time", "1-2周"),
                "learning_objectives": [
                    f"掌握{gap['skill']}的基本概念",
                    f"完成{gap['skill']}的实战项目"
                ],
                "prerequisites": gap.get("prerequisites", []),
                "resources": gap.get("learning_resources", [])
            }
            
            if gap["skill"] in current_skill_set:
                stage["status"] = "completed"
            elif any(p in current_skill_set for p in gap.get("prerequisites", [])):
                stage["status"] = "ready"
            else:
                stage["status"] = "pending"
            
            roadmap.append(stage)
        
        return roadmap

    def _generate_interview_prep(self, 
                                 matched_skills: List[str], 
                                 missing_skills: List[str], 
                                 job_profile: Dict[str, Any]) -> Dict[str, Any]:
        prep = {
            "strengths_to_highlight": [],
            "areas_to_prepare": [],
            "questions_to_expect": [],
            "tips": []
        }
        
        for skill in matched_skills[:3]:
            prep["strengths_to_highlight"].append({
                "skill": skill,
                "question": f"请介绍一下您在{skill}方面的项目经验",
                "focus": "技术深度和实际应用"
            })
        
        for skill in missing_skills[:2]:
            prep["areas_to_prepare"].append({
                "skill": skill,
                "question": f"您对{skill}有多少了解？是否有学习计划？",
                "strategy": "诚实面对差距，展示学习热情"
            })
        
        if job_profile.get("job_responsibilities"):
            prep["questions_to_expect"].append({
                "topic": "岗位职责",
                "question": "请描述您对岗位职责的理解"
            })
        
        prep["tips"] = [
            "突出与岗位匹配的核心技能",
            "诚实面对技能差距，展现学习能力",
            "准备具体项目案例支撑技能陈述",
            "了解公司业务，展示文化匹配度"
        ]
        
        return prep

    def _analyze_career_progression(self, current_skills: List[str], target_skills: List[str], db=None) -> Dict:
        progression = {
            "current_level": "unknown",
            "target_level": "unknown",
            "skill_gap": [],
            "time_estimate": "unknown",
            "milestones": []
        }
        
        try:
            if db:
                current_level = self._estimate_skill_level(current_skills, db)
                target_level = self._estimate_skill_level(target_skills, db)
            else:
                current_level = self._estimate_skill_level(current_skills)
                target_level = self._estimate_skill_level(target_skills)
            
            progression["current_level"] = current_level
            progression["target_level"] = target_level
            
            missing_for_target = set(target_skills) - set(current_skills)
            progression["skill_gap"] = list(missing_for_target)
            
            total_difficulty = sum([
                1 if db and self._get_skill_difficulty(s, db) == "easy" else
                2 if db and self._get_skill_difficulty(s, db) == "medium" else 3
                for s in missing_for_target
            ])
            
            weeks_estimate = total_difficulty * 2
            progression["time_estimate"] = f"约{weeks_estimate}周"
            
            milestones = []
            for i, skill in enumerate(list(missing_for_target)[:3]):
                milestones.append({
                    "skill": skill,
                    "target_week": weeks_estimate * (i + 1) // 3
                })
            progression["milestones"] = milestones
            
        except Exception as e:
            print(f"[MatchAgent] Career progression analysis error: {e}")
        
        return progression

    def _estimate_skill_level(self, skills: List[str], db=None) -> str:
        if not skills:
            return "入门"
        
        advanced_keywords = ["架构", "架构师", "高级", "资深", "专家", "lead", "senior"]
        intermediate_keywords = ["熟练", "掌握", "精通", "proficient"]
        
        advanced_count = sum(1 for s in skills if any(k in s.lower() for k in advanced_keywords))
        intermediate_count = sum(1 for s in skills if any(k in s.lower() for k in intermediate_keywords))
        
        if advanced_count > len(skills) * 0.3:
            return "专家"
        elif intermediate_count > len(skills) * 0.5:
            return "熟练"
        else:
            return "初级"

    def _get_skill_difficulty(self, skill: str, db=None) -> str:
        try:
            if db:
                kb_skill = self.knowledge_base.get_skill_by_name(skill, db=db)
            else:
                kb_skill = self.knowledge_base.get_skill_by_name(skill)
            
            if kb_skill:
                return kb_skill.get("difficulty", "medium")
        except:
            pass
        return "medium"

    def _calculate_experience_match(self, resume_profile, job_profile):
        resume_exp = self._parse_experience_years(resume_profile.get("experience_years", "0年"))
        job_exp = self._parse_experience_years(job_profile.get("required_experience", "0年"))
        
        if job_exp == 0:
            return 100
        
        if resume_exp >= job_exp:
            return 100
        elif resume_exp >= job_exp * 0.5:
            return 60
        else:
            return min((resume_exp / job_exp) * 100, 40)
    
    def _parse_experience_years(self, experience_str):
        if not experience_str:
            return 0
        import re
        match = re.search(r'(\d+)', str(experience_str))
        return int(match.group(1)) if match else 0
    
    def _calculate_education_match(self, resume_profile, job_profile):
        edu_levels = {'高中': 1, '大专': 2, '本科': 3, '硕士': 4, '博士': 5}
        
        resume_edu = resume_profile.get("education", "")
        job_edu = job_profile.get("required_education", "")
        
        resume_level = 0
        job_level = 0
        
        for level, score in edu_levels.items():
            if level in resume_edu:
                resume_level = score
            if level in job_edu:
                job_level = score
        
        if job_level == 0:
            return 100
        
        if resume_level >= job_level:
            return 100
        elif resume_level == job_level - 1:
            return 70
        else:
            return 40
    
    def _calculate_certificate_match(self, resume_profile, job_profile):
        resume_certs = resume_profile.get("highlights", [])
        return 80 if len(resume_certs) > 0 else 50
    
    def _calculate_location_match(self, resume_profile, job_profile):
        resume_loc = resume_profile.get("location", "")
        job_loc = job_profile.get("location", "")
        
        if not job_loc or job_loc == "未提供":
            return 100
        
        if resume_loc and job_loc in resume_loc or resume_loc in job_loc:
            return 100
        
        return 60
    
    def _apply_education_penalty(self, base_score: float, resume_profile: Dict, job_profile: Dict, penalty_rules: str) -> Dict:
        """
        应用学历惩罚
        penalty_rules格式：JSON字符串，例如：
        {
            "penalties": [
                {"gap": 1, "factor": 0.9},
                {"gap": 2, "factor": 0.8},
                {"gap": 3, "factor": 0.7}
            ]
        }
        """
        try:
            import json
            rules = json.loads(penalty_rules)
        except:
            # 如果解析失败，不惩罚
            return {"final_score": base_score, "penalty_factor": 1.0, "applied": False}
        
        # 计算学历等级差距
        edu_levels = {"高中": 1, "大专": 2, "本科": 3, "硕士": 4, "博士": 5}
        
        resume_edu = resume_profile.get("education", "")
        job_edu = job_profile.get("required_education", job_profile.get("education_level", ""))
        
        resume_level = 0
        job_level = 0
        
        for level, score in edu_levels.items():
            if level in resume_edu:
                resume_level = score
            if level in job_edu:
                job_level = score
        
        # 如果没有要求或者学历达标，不惩罚
        if job_level == 0 or resume_level >= job_level:
            return {"final_score": base_score, "penalty_factor": 1.0, "applied": False}
        
        # 计算学历差距
        edu_gap = job_level - resume_level
        
        # 获取惩罚因子
        penalty_factor = 1.0
        if "penalties" in rules:
            for penalty in rules["penalties"]:
                if penalty.get("gap") == edu_gap:
                    penalty_factor = penalty.get("factor", 1.0)
                    break
        
        # 应用惩罚
        final_score = base_score * penalty_factor
        
        return {
            "final_score": final_score,
            "penalty_factor": penalty_factor,
            "applied": penalty_factor < 1.0
        }
    
    def get_recommendations(self, user_id: str, user_role: str, db=None) -> List:
        return []

    def record_match_feedback(self, resume_id: int, job_id: int, is_positive: bool, 
                              resume_profile: Dict, job_profile: Dict, db=None):
        """记录匹配反馈，用于权重学习"""
        from datetime import datetime
        from modules.agents.weight_learner import LearningSample

        # 重新计算各维度分数作为样本
        resume_skills = set(resume_profile.get("skills", []))
        job_skills = set(job_profile.get("required_skills", []))
        
        skill_score, _, _ = self._calculate_skill_match(resume_skills, job_skills, db)
        dimension_scores = {
            'skills': skill_score / 100.0,
            'experience': self._calculate_experience_match(resume_profile, job_profile) / 100.0,
            'education': self._calculate_education_match(resume_profile, job_profile) / 100.0,
            'certificates': self._calculate_certificate_match(resume_profile, job_profile) / 100.0,
            'location': self._calculate_location_match(resume_profile, job_profile) / 100.0
        }

        sample = LearningSample(
            resume_id=resume_id,
            job_id=job_id,
            match_score=self.calculate_match(resume_profile, job_profile, db)["match_score"] / 100.0,
            dimension_scores=dimension_scores,
            is_positive=is_positive,
            timestamp=datetime.now()
        )

        self.weight_learner.add_sample(sample)
        print(f"[MatchAgent] 反馈记录已添加: resume={resume_id}, job={job_id}, positive={is_positive}")

    def trigger_weight_learning(self):
        """触发权重学习"""
        print("[MatchAgent] 开始权重学习...")
        new_weights = self.weight_learner.learn_weights()
        self.weights = new_weights.to_dict()
        return new_weights

    def get_weight_report(self) -> Dict:
        """获取权重报告"""
        return self.weight_learner.export_weight_report()

    def adjust_weights_manually(self, adjustments: Dict[str, float]):
        """手动调整权重"""
        self.weight_learner.manual_adjust_weights(adjustments)
        self.weights = self.weight_learner.current_weights.to_dict()

    def get_industry_weights(self, industry: str) -> Dict[str, float]:
        """获取行业特定权重"""
        return self.weight_learner.get_industry_specific_weights(industry).to_dict()
