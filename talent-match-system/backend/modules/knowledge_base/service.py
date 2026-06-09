"""
知识库服务模块
提供统一的API接口供Agent调用
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from difflib import SequenceMatcher

from .db import KnowledgeBaseDB
from .graph import SkillKnowledgeGraph
from .parsers import DataNormalizer
from .vector_db import get_vector_db

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    知识库服务类
    提供技能查询、关系推理、趋势分析等核心功能
    """

    def __init__(self, db_path: Optional[str] = None, graph_path: Optional[str] = None):
        self.db = KnowledgeBaseDB(db_path)
        self.graph = SkillKnowledgeGraph()
        self.normalizer = DataNormalizer()
        self.vector_db = get_vector_db()

        if graph_path:
            self.graph.load_graph(graph_path)
        else:
            self._try_load_graph()

        self._sync_skills_to_vector_db()

        self.logger = logger

    def _sync_skills_to_vector_db(self) -> None:
        """同步技能数据到向量数据库"""
        if not self.vector_db.is_available():
            logger.info("Vector database not available, skipping sync")
            return
            
        try:
            db_count = self.db.get_skill_count()
            vector_count = self.vector_db.count()

            if vector_count == 0 or db_count > vector_count:
                logger.info("Syncing skills to vector database...")
                skills = self.db.get_all_skills()
                skill_dicts = []
                for skill in skills:
                    skill_dict = {
                        "id": str(skill["skill_id"]),
                        "name": skill["skill_name"],
                        "description": skill.get("description", skill["skill_name"]),
                        "category": skill.get("category", ""),
                        "parent_id": skill.get("parent_id", ""),
                        "related_skills": []
                    }
                    skill_dicts.append(skill_dict)

                self.vector_db.add_skills(skill_dicts)
                logger.info(f"Synced {len(skill_dicts)} skills to vector database")
        except Exception as e:
            logger.warning(f"Failed to sync skills to vector database: {e}")

    def _try_load_graph(self) -> bool:
        """尝试加载图谱"""
        data_dir = Path(__file__).parent / "data"
        graph_file = data_dir / "skill_graph.gpickle"

        if graph_file.exists():
            return self.graph.load_graph(str(graph_file))

        skills = self.db.get_all_skills()
        relations = self.db.get_all_relations()

        for skill in skills:
            self.graph.add_skill_node(skill['skill_id'], skill)

        for rel in relations:
            self.graph.add_skill_relation(
                rel['skill_id_1'],
                rel['skill_id_2'],
                rel['relation_type'],
                rel['weight']
            )

        return True

    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """
        获取技能详细信息

        Args:
            skill_name: 技能名称

        Returns:
            技能信息字典
        """
        normalized = self.normalizer.normalize_skill_name(skill_name)
        skill = self.db.get_skill_by_name(normalized)

        if not skill:
            skill = self.db.get_skill_by_alias(skill_name)

        if skill:
            relations = self.db.get_skill_relations(skill['skill_id'])
            skill['relations'] = relations

            if skill.get('skill_aliases'):
                try:
                    skill['skill_aliases'] = json.loads(skill['skill_aliases'])
                except:
                    skill['skill_aliases'] = []

        return skill

    def normalize_skill(self, raw_skill_name: str) -> Dict[str, Any]:
        """
        标准化技能名称

        Args:
            raw_skill_name: 原始技能名称

        Returns:
            标准化结果字典
        """
        normalized = self.normalizer.normalize_skill_name(raw_skill_name)

        skill = self.db.get_skill_by_name(normalized)
        if skill:
            return {
                'normalized': skill['skill_name'],
                'confidence': 1.0,
                'skill_id': skill['skill_id'],
                'category': skill.get('category'),
                'status': 'exact_match'
            }

        skill = self.db.get_skill_by_alias(raw_skill_name)
        if skill:
            return {
                'normalized': skill['skill_name'],
                'confidence': 0.95,
                'skill_id': skill['skill_id'],
                'category': skill.get('category'),
                'status': 'alias_match'
            }

        similar = self._fuzzy_match_skill(raw_skill_name)
        if similar:
            return {
                'normalized': similar['skill_name'],
                'confidence': similar['similarity'],
                'skill_id': similar['skill_id'],
                'category': similar.get('category'),
                'status': 'fuzzy_match'
            }

        return {
            'normalized': normalized,
            'confidence': 0.0,
            'skill_id': None,
            'category': self.normalizer.detect_category(normalized),
            'status': 'not_found'
        }

    def _fuzzy_match_skill(self, skill_name: str, threshold: float = 0.6) -> Optional[Dict]:
        """
        模糊匹配技能

        Args:
            skill_name: 技能名称
            threshold: 相似度阈值

        Returns:
            最匹配的技能
        """
        all_skills = self.db.get_all_skills()

        normalized = self.normalizer.normalize_skill_name(skill_name)
        best_match = None
        best_similarity = 0

        for skill in all_skills:
            skill_name_db = skill['skill_name']

            similarity = SequenceMatcher(None, normalized.lower(), skill_name_db.lower()).ratio()

            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = skill

        if best_match:
            best_match['similarity'] = best_similarity

        return best_match

    def get_related_skills(self, skill_id: int, max_count: int = 10,
                          relation_type: Optional[str] = None) -> List[Dict]:
        """
        获取相关技能

        Args:
            skill_id: 技能ID
            max_count: 最大返回数量
            relation_type: 关系类型过滤

        Returns:
            相关技能列表
        """
        related = self.graph.get_related_skills(skill_id, max_depth=2,
                                               relation_type=relation_type)

        if relation_type:
            return related[:max_count]

        result = []
        seen_categories = set()

        for rel in related:
            category = rel.get('category', '其他')
            if category not in seen_categories or len(result) < max_count // 2:
                result.append(rel)
                seen_categories.add(category)

            if len(result) >= max_count:
                break

        return result

    def get_skill_learning_path(self, from_skill: str, to_skill: str) -> Optional[List[Dict]]:
        """
        获取技能学习路径

        Args:
            from_skill: 起始技能名称
            to_skill: 目标技能名称

        Returns:
            学习路径列表
        """
        from_normalized = self.normalize_skill(from_skill)
        to_normalized = self.normalize_skill(to_skill)

        if not from_normalized['skill_id'] or not to_normalized['skill_id']:
            return None

        return self.graph.get_skill_learning_path(
            from_normalized['skill_id'],
            to_normalized['skill_id']
        )

    def enhance_match(self, resume_skills: List[str],
                     job_skills: List[str]) -> Dict[str, Any]:
        """
        增强人岗匹配

        Args:
            resume_skills: 简历技能列表
            job_skills: 岗位技能列表

        Returns:
            增强匹配结果
        """
        resume_normalized = [self.normalize_skill(s) for s in resume_skills]
        job_normalized = [self.normalize_skill(s) for s in job_skills]

        direct_matches = []
        missing_skills = []

        for job_skill in job_normalized:
            if job_skill['skill_id'] is None:
                continue

            matched = False
            for resume_skill in resume_normalized:
                if resume_skill['skill_id'] == job_skill['skill_id']:
                    direct_matches.append({
                        'skill': job_skill['normalized'],
                        'skill_id': job_skill['skill_id'],
                        'match_type': 'direct',
                        'confidence': 1.0
                    })
                    matched = True
                    break

            if not matched:
                missing_skills.append(job_skill)

        related_matches = []
        for missing in missing_skills:
            if missing['skill_id'] is None:
                continue

            related = self.get_related_skills(missing['skill_id'], max_count=5)

            for rel_skill in related:
                for resume_skill in resume_normalized:
                    if resume_skill['skill_id'] == rel_skill['skill_id']:
                        related_matches.append({
                            'job_skill': missing['normalized'],
                            'job_skill_id': missing['skill_id'],
                            'resume_skill': resume_skill['normalized'],
                            'resume_skill_id': resume_skill['skill_id'],
                            'relation': rel_skill.get('relation_type', 'similar'),
                            'confidence': rel_skill.get('weight', 0.5)
                        })
                        break

        direct_score = len(direct_matches) / len(job_normalized) if job_normalized else 0
        related_score = len(related_matches) / len(missing_skills) if missing_skills else 0
        enhanced_score = direct_score * 0.8 + related_score * 0.2

        return {
            'direct_matches': direct_matches,
            'related_matches': related_matches,
            'missing_skills': [s['normalized'] for s in missing_skills if s['skill_id']],
            'unrecognized_skills': [s['normalized'] for s in missing_skills if not s['skill_id']],
            'direct_score': round(direct_score * 100, 2),
            'related_score': round(related_score * 100, 2),
            'enhanced_score': round(enhanced_score * 100, 2),
            'total_job_skills': len(job_normalized),
            'matched_count': len(direct_matches),
            'related_count': len(related_matches)
        }

    def get_skill_trend(self, skill_name: str,
                       start_period: Optional[str] = None,
                       end_period: Optional[str] = None) -> Dict[str, Any]:
        """
        获取技能需求趋势

        Args:
            skill_name: 技能名称
            start_period: 开始时间
            end_period: 结束时间

        Returns:
            趋势数据
        """
        normalized = self.normalize_skill(skill_name)

        if not normalized['skill_id']:
            return {
                'skill_name': skill_name,
                'skill_id': None,
                'trend': [],
                'message': '技能未在知识库中找到'
            }

        trend = self.db.get_skill_demand_trend(
            normalized['skill_id'],
            start_period,
            end_period
        )

        if not trend:
            return {
                'skill_name': skill_name,
                'skill_id': normalized['skill_id'],
                'trend': [],
                'message': '暂无趋势数据'
            }

        trend_data = [
            {
                'time_period': t['time_period'],
                'demand_value': t['demand_value'],
                'proportion': t.get('proportion_value')
            }
            for t in trend
        ]

        return {
            'skill_name': skill_name,
            'skill_id': normalized['skill_id'],
            'trend': trend_data,
            'avg_demand': sum(t['demand_value'] for t in trend) / len(trend),
            'max_demand': max(t['demand_value'] for t in trend),
            'data_points': len(trend)
        }

    def get_skill_recommendations(self, skill_name: str,
                                 target_role: Optional[str] = None,
                                 limit: int = 10) -> List[Dict]:
        """
        获取技能推荐

        Args:
            skill_name: 基础技能名称
            target_role: 目标职业（可选）
            limit: 推荐数量

        Returns:
            推荐技能列表
        """
        normalized = self.normalize_skill(skill_name)

        if not normalized['skill_id']:
            return []

        recommendations = []

        related = self.graph.get_related_skills(normalized['skill_id'], max_depth=2)

        for rel in related[:limit * 2]:
            if rel['skill_id'] == normalized['skill_id']:
                continue

            recommendations.append({
                'skill_name': rel.get('skill_name', f'skill_{rel["skill_id"]}'),
                'skill_id': rel['skill_id'],
                'relation_type': rel.get('relation_type'),
                'relevance': rel.get('weight', 0.5),
                'category': rel.get('category'),
                'suggestion': self._generate_skill_suggestion(
                    skill_name,
                    rel.get('skill_name', f'skill_{rel["skill_id"]}'),
                    rel.get('relation_type')
                )
            })

        recommendations.sort(key=lambda x: x['relevance'], reverse=True)

        return recommendations[:limit]

    def _generate_skill_suggestion(self, base_skill: str,
                                   target_skill: str,
                                   relation_type: str) -> str:
        """生成技能建议文本"""
        suggestions = {
            'co_occurrence': f'与{base_skill}经常一起使用',
            'similar': f'{base_skill}的相似技能',
            'prerequisite': f'{base_skill}的前置技能',
            'same_category': f'同{base_skill}类别的技能',
            'required_for': f'学习{base_skill}后可以掌握'
        }

        return suggestions.get(relation_type, f'推荐学习{target_skill}')

    def search_skills(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索技能

        Args:
            keyword: 搜索关键词
            limit: 返回数量

        Returns:
            匹配的技能列表
        """
        return self.db.search_skills(keyword, limit)

    def get_hot_skills(self, limit: int = 50) -> List[Dict]:
        """
        获取热门技能

        Args:
            limit: 返回数量

        Returns:
            热门技能列表
        """
        return self.db.get_hot_skills(limit)

    def get_skill_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            统计信息字典
        """
        stats = self.graph.get_skill_graph_stats()
        stats['db_skill_count'] = self.db.get_skill_count()
        stats['db_relation_count'] = self.db.get_relation_count()

        return stats

    def save_knowledge_graph(self):
        """保存知识图谱"""
        self.graph.save_graph()

    def close(self):
        """关闭数据库连接"""
        self.db.close()

    def semantic_search_skills(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        语义搜索技能
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
        
        Returns:
            相似技能列表，按相似度排序
        """
        if not query.strip():
            return []

        if not self.vector_db.is_available():
            logger.info("Vector database not available, falling back to keyword search")
            return self.db.search_skills(query, top_k)

        results = self.vector_db.search_similar(query, top_k)
        
        for result in results:
            skill_info = self.db.get_skill_by_name(result["name"])
            if skill_info:
                result["skill_id"] = skill_info["skill_id"]
                result["description"] = skill_info.get("description", result["description"])
        
        return results

    def fuzzy_search_skills(self, query: str, threshold: float = 0.6, limit: int = 10) -> List[Dict[str, Any]]:
        """
        综合模糊搜索（结合关键词匹配和语义搜索）
        
        Args:
            query: 搜索查询
            threshold: 相似度阈值
            limit: 返回数量
        
        Returns:
            匹配的技能列表
        """
        keyword_results = self.db.search_skills(query, limit)
        
        if not self.vector_db.is_available():
            return keyword_results
        
        semantic_results = self.semantic_search_skills(query, limit)

        combined = []
        seen_names = set()

        for result in keyword_results:
            if result["skill_name"] not in seen_names:
                combined.append({
                    "skill_id": result["skill_id"],
                    "name": result["skill_name"],
                    "category": result.get("category"),
                    "description": result.get("description"),
                    "score": 1.0,
                    "match_type": "keyword"
                })
                seen_names.add(result["skill_name"])

        for result in semantic_results:
            if result["name"] not in seen_names and result["score"] >= threshold:
                combined.append({
                    "skill_id": result.get("skill_id"),
                    "name": result["name"],
                    "category": result.get("category"),
                    "description": result.get("description"),
                    "score": result["score"],
                    "match_type": "semantic"
                })
                seen_names.add(result["name"])

        combined.sort(key=lambda x: x["score"], reverse=True)
        
        return combined[:limit]
