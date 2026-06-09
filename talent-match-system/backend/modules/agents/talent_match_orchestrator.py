"""人才匹配业务编排器"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .resume_agent import ResumeParseAgent
from .ability_analysis_agent import AbilityAnalysisAgent
from .job_agent import JobParseAgent
from .match_agent import MatchAgent

logger = logging.getLogger(__name__)


class TalentMatchOrchestrator:
    """人才匹配业务编排器"""
    
    def __init__(self):
        self.resume_agent = ResumeParseAgent()
        self.ability_agent = AbilityAnalysisAgent()
        self.job_agent = JobParseAgent()
        self.match_agent = MatchAgent()
        
        logger.info("TalentMatchOrchestrator initialized")
    
    def process_resume(self, file_path: str, db=None) -> Dict[str, Any]:
        """处理简历上传和解析"""
        logger.info(f"Processing resume: {file_path}")
        
        try:
            resume_data = self.resume_agent.parse_resume_from_file(file_path, db)
            return {
                "success": True,
                "resume_data": resume_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Resume processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_ability(self, resume_data: Dict[str, Any], user_id: str, resume_id: Optional[str] = None) -> Dict[str, Any]:
        """生成完整的能力分析报告"""
        logger.info(f"Generating ability analysis for user {user_id}")
        
        try:
            analysis_result = self.ability_agent.analyze_ability(resume_data, user_id, resume_id)
            return {
                "success": True,
                "data": analysis_result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Ability analysis failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def match_jobs(self, resume_data: Dict[str, Any], job_ids: list, db=None) -> Dict[str, Any]:
        """将简历与多个岗位进行匹配"""
        logger.info(f"Matching resume with {len(job_ids)} jobs")
        
        match_results = []
        
        try:
            for job_id in job_ids:
                job_data = self._get_job_data(job_id, db)
                
                if not job_data:
                    match_results.append({
                        "job_id": job_id,
                        "success": False,
                        "error": "Job not found"
                    })
                    continue
                
                match_result = self.match_agent.calculate_match(resume_data, job_data, db)
                
                match_results.append({
                    "job_id": job_id,
                    "job_title": job_data.get("job_title", "未提供"),
                    "success": True,
                    "data": match_result
                })
            
            return {
                "success": True,
                "results": match_results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Job matching failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "results": match_results,
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_job_data(self, job_id: int, db) -> Optional[Dict[str, Any]]:
        """获取岗位数据"""
        try:
            return {
                "job_title": "未提供",
                "required_skills": [],
                "required_education": "",
                "required_experience": 0
            }
        except Exception as e:
            logger.warning(f"Failed to get job data: {e}")
            return None
    
    def execute_full_workflow(self, file_path: str, job_ids: Optional[list] = None, user_id: str = "default", db=None) -> Dict[str, Any]:
        """执行完整的业务流程"""
        logger.info(f"Starting full workflow for user {user_id}")
        
        result = {
            "workflow": "talent_match_full",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "steps": []
        }
        
        # Step 1: 解析简历
        step1_result = self.process_resume(file_path, db)
        result["steps"].append({
            "step": "resume_parsing",
            "success": step1_result["success"],
            "data": step1_result.get("resume_data") if step1_result["success"] else None,
            "error": step1_result.get("error")
        })
        
        if not step1_result["success"]:
            result["success"] = False
            return result
        
        resume_data = step1_result["resume_data"]
        
        # Step 2: 生成能力分析
        step2_result = self.analyze_ability(resume_data, user_id)
        result["steps"].append({
            "step": "ability_analysis",
            "success": step2_result["success"],
            "data": step2_result.get("data") if step2_result["success"] else None,
            "error": step2_result.get("error")
        })
        
        if step2_result["success"]:
            result["ability_tree"] = step2_result["data"]["ability_tree"]
            result["radar_chart"] = step2_result["data"]["radar_chart"]
            result["text_analysis"] = step2_result["data"]["text_analysis"]
        
        # Step 3: 岗位匹配（可选）
        if job_ids:
            step3_result = self.match_jobs(resume_data, job_ids, db)
            result["steps"].append({
                "step": "job_matching",
                "success": step3_result["success"],
                "data": step3_result.get("results") if step3_result["success"] else None,
                "error": step3_result.get("error")
            })
            
            if step3_result["success"]:
                result["job_matches"] = step3_result["results"]
        
        result["success"] = all(step["success"] for step in result["steps"])
        logger.info(f"Full workflow completed: {result['success']}")
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "status": "healthy",
            "orchestrator": "TalentMatchOrchestrator",
            "agents": {
                "resume_agent": "active",
                "ability_agent": "active",
                "job_agent": "active",
                "match_agent": "active"
            },
            "timestamp": datetime.now().isoformat()
        }
