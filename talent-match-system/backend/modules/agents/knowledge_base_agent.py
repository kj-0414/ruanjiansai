"""
知识库Agent
基于知识库服务的智能Agent
"""

import logging
from typing import List, Dict, Optional, Any

from modules.knowledge_base.service import KnowledgeBaseService

logger = logging.getLogger(__name__)


class KnowledgeBaseAgent:
    """
    知识库Agent
    提供基于知识库的智能查询和建议功能
    """

    def __init__(self):
        self.kb_service = KnowledgeBaseService()
        self.logger = logger

    def query_skill(self, skill_name: str) -> Dict[str, Any]:
        """
        查询技能信息

        Args:
            skill_name: 技能名称

        Returns:
            技能详细信息
        """
        self.logger.info(f"🔍 查询技能: {skill_name}")

        result = {
            'skill_name': skill_name,
            'found': False,
            'data': None,
            'related_skills': []
        }

        skill_info = self.kb_service.get_skill_info(skill_name)

        if skill_info:
            result['found'] = True
            result['data'] = skill_info

            related = self.kb_service.get_related_skills(
                skill_info['skill_id'],
                max_count=5
            )
            result['related_skills'] = [
                {
                    'name': r.get('skill_name'),
                    'relation': r.get('relation_type'),
                    'relevance': r.get('weight', 0)
                }
                for r in related
            ]

        return result

    def normalize_skills(self, skills: List[str]) -> List[Dict[str, Any]]:
        """
        批量标准化技能名称

        Args:
            skills: 技能名称列表

        Returns:
            标准化结果列表
        """
        self.logger.info(f"🔄 标准化 {len(skills)} 个技能")

        results = []
        for skill in skills:
            normalized = self.kb_service.normalize_skill(skill)
            results.append(normalized)

        return results

    def get_learning_path(self, from_skill: str, to_skill: str) -> Optional[List[Dict]]:
        """
        获取技能学习路径

        Args:
            from_skill: 起始技能
            to_skill: 目标技能

        Returns:
            学习路径
        """
        self.logger.info(f"🛤️ 查询学习路径: {from_skill} → {to_skill}")

        path = self.kb_service.get_skill_learning_path(from_skill, to_skill)

        if path:
            return [
                {
                    'step': p['step'],
                    'name': p.get('name', p.get('skill_name')),
                    'relation': p.get('relation_type')
                }
                for p in path
            ]

        return None

    def recommend_skills(self, base_skills: List[str],
                        target_role: Optional[str] = None,
                        limit: int = 10) -> List[Dict]:
        """
        推荐相关技能

        Args:
            base_skills: 基础技能列表
            target_role: 目标职业
            limit: 推荐数量

        Returns:
            推荐技能列表
        """
        self.logger.info(f"💡 基于 {len(base_skills)} 个技能生成推荐")

        all_recommendations = {}

        for skill in base_skills:
            recommendations = self.kb_service.get_skill_recommendations(
                skill,
                target_role=target_role,
                limit=limit
            )

            for rec in recommendations:
                skill_id = rec['skill_id']
                if skill_id not in all_recommendations:
                    all_recommendations[skill_id] = {
                        **rec,
                        'support_count': 1,
                        'supported_by': [skill]
                    }
                else:
                    all_recommendations[skill_id]['support_count'] += 1
                    all_recommendations[skill_id]['supported_by'].append(skill)

        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: (x['support_count'], x['relevance']),
            reverse=True
        )

        return sorted_recommendations[:limit]

    def enhance_resume_skills(self, resume_skills: List[str]) -> Dict[str, Any]:
        """
        增强简历技能

        Args:
            resume_skills: 简历中的技能列表

        Returns:
            增强结果
        """
        self.logger.info(f"📄 增强 {len(resume_skills)} 个简历技能")

        normalized = self.kb_service.normalize_skills(resume_skills)

        found_skills = [n['normalized'] for n in normalized if n['confidence'] > 0]
        not_found_skills = [n['normalized'] for n in normalized if n['confidence'] == 0]

        recommendations = []
        if found_skills:
            recommendations = self.kb_service.get_skill_recommendations(
                found_skills[0],
                limit=5
            )

        return {
            'original_count': len(resume_skills),
            'normalized_count': len(found_skills),
            'found_skills': found_skills,
            'not_found_skills': not_found_skills,
            'recommendations': recommendations,
            'coverage_rate': len(found_skills) / len(resume_skills) * 100 if resume_skills else 0
        }

    def get_skill_trends(self, skill_names: List[str]) -> Dict[str, Any]:
        """
        批量获取技能趋势

        Args:
            skill_names: 技能名称列表

        Returns:
            趋势数据
        """
        self.logger.info(f"📈 获取 {len(skill_names)} 个技能的趋势")

        trends = {}
        for skill_name in skill_names:
            trend = self.kb_service.get_skill_trend(skill_name)
            if trend.get('trend'):
                trends[skill_name] = trend

        return {
            'total_skills': len(skill_names),
            'with_trends': len(trends),
            'trends': trends
        }

    def search_skills_by_keyword(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        关键词搜索技能

        Args:
            keyword: 搜索关键词
            limit: 返回数量

        Returns:
            匹配的技能列表
        """
        return self.kb_service.search_skills(keyword, limit)

    def get_hot_skills(self, limit: int = 50) -> List[Dict]:
        """
        获取热门技能

        Args:
            limit: 返回数量

        Returns:
            热门技能列表
        """
        return self.kb_service.get_hot_skills(limit)

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            统计信息
        """
        return self.kb_service.get_skill_statistics()

    def close(self):
        """关闭连接"""
        self.kb_service.close()
