"""
人才智能匹配系统 - 知识库模块
基于 Job-SDF 数据集构建职业技能知识图谱
"""

__version__ = "1.0.0"
__author__ = "Talent Match System Team"

from .db import KnowledgeBaseDB
from .graph import SkillKnowledgeGraph
from .service import KnowledgeBaseService

__all__ = [
    'KnowledgeBaseDB',
    'SkillKnowledgeGraph',
    'KnowledgeBaseService',
]
