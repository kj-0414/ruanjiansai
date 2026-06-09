
"""
Job-SDF 数据集集成模块
提供数据驱动的权重和技能需求信息
"""
import json
from pathlib import Path
from typing import Dict, Optional
import pandas as pd


class JobSDFIntegration:
    """
    Job-SDF 数据集集成类
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        初始化 Job-SDF 集成
        
        Args:
            data_dir: 数据目录路径，默认为项目根目录下的 data/job_sdf
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / 'data' / 'job_sdf'
        
        self.data_dir = Path(data_dir)
        self.config = self._load_config()
        self.skill_weights = self._load_skill_weights()
        self.recommended_weights = self._load_recommended_weights()
        
    def _load_config(self) -> Dict:
        """
        加载集成配置
        
        Returns:
            配置字典
        """
        config_file = self.data_dir / 'integration_config.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def _load_skill_weights(self) -> Dict:
        """
        加载技能权重
        
        Returns:
            技能权字典
        """
        weight_file = self.data_dir / 'skill_weights.json'
        if weight_file.exists():
            with open(weight_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def _load_recommended_weights(self) -> Dict:
        """
        加载推荐的匹配维度权重
        
        Returns:
            权重字典
        """
        # 默认权重
        default_weights = {
            'skills': 0.40,
            'experience': 0.25,
            'education': 0.15,
            'certificates': 0.10,
            'location': 0.10
        }
        
        # 尝试从配置加载
        if 'recommended_weights' in self.config:
            return self.config['recommended_weights']
        
        # 尝试从文件加载
        weight_file = self.data_dir / 'recommended_matching_weights.json'
        if weight_file.exists():
            with open(weight_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return default_weights
    
    def get_matching_weights(self) -> Dict[str, float]:
        """
        获取推荐的匹配维度权重
        
        Returns:
            权重字典
        """
        return self.recommended_weights.copy()
    
    def get_skill_importance(self, skill_id: int) -> Optional[Dict]:
        """
        获取技能重要性信息
        
        Args:
            skill_id: 技能ID
            
        Returns:
            技能重要性信息字典
        """
        skill_key = str(skill_id)
        if skill_key in self.skill_weights:
            return self.skill_weights[skill_key]
        
        # 也尝试整数键
        if skill_id in self.skill_weights:
            return self.skill_weights[skill_id]
            
        return None
    
    def get_composite_weight(self, skill_id: int) -> float:
        """
        获取技能的综合权重
        
        Args:
            skill_id: 技能ID
            
        Returns:
            综合权重值
        """
        info = self.get_skill_importance(skill_id)
        if info:
            return info.get('composite_weight', 0.0)
        return 0.0
    
    def get_demand_weight(self, skill_id: int) -> float:
        """
        获取技能的需求权重
        
        Args:
            skill_id: 技能ID
            
        Returns:
            需求权重值
        """
        info = self.get_skill_importance(skill_id)
        if info:
            return info.get('demand_weight', 0.0)
        return 0.0


# 全局单例
_job_sdf_instance: Optional[JobSDFIntegration] = None


def get_job_sdf() -> JobSDFIntegration:
    """
    获取 Job-SDF 集成单例
    
    Returns:
        JobSDFIntegration 实例
    """
    global _job_sdf_instance
    if _job_sdf_instance is None:
        _job_sdf_instance = JobSDFIntegration()
    return _job_sdf_instance


def get_data_driven_weights() -> Dict[str, float]:
    """
    获取数据驱动的匹配维度权重（便捷函数）
    
    Returns:
        权重字典
    """
    return get_job_sdf().get_matching_weights()

