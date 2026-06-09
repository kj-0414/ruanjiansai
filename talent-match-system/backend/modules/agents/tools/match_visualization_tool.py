"""
技能匹配可视化工具
用于生成人岗匹配的热力图数据
"""

from typing import Dict, Any, List
import logging

from modules.agents.tools.base import BaseTool

logger = logging.getLogger(__name__)


class MatchVisualizationTool(BaseTool):
    """技能匹配可视化工具"""
    
    def __init__(self):
        super().__init__(
            name="match_visualization",
            description="生成人岗匹配可视化数据",
            parameters={
                "resume_skills": {"type": "array", "description": "简历技能列表"},
                "job_skills": {"type": "array", "description": "岗位技能列表"},
                "match_scores": {"type": "object", "description": "匹配分数详情"}
            }
        )
    
    def run(self, resume_skills: List[str], job_skills: List[str], match_scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成匹配可视化数据
        
        Args:
            resume_skills: 简历技能列表
            job_skills: 岗位技能列表
            match_scores: 匹配分数详情
        
        Returns:
            可视化数据（热力图、雷达图、技能差距）
        """
        try:
            # 生成热力图数据
            heatmap_data = self._generate_heatmap_data(resume_skills, job_skills)
            
            # 生成雷达图数据
            radar_data = self._generate_radar_data(match_scores)
            
            # 生成技能差距分析
            gap_data = self._generate_gap_analysis(resume_skills,