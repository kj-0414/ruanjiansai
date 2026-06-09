"""
图数据加载器
将技能关系图数据加载到知识库
"""

import logging
import pandas as pd
from typing import List, Dict
from pathlib import Path

from ..db import KnowledgeBaseDB
from ..graph import SkillKnowledgeGraph
from ..parsers import ParquetParser

logger = logging.getLogger(__name__)


class GraphLoader:
    """图数据加载器"""

    def __init__(self, db: KnowledgeBaseDB, graph: SkillKnowledgeGraph, data_dir: str):
        self.db = db
        self.graph = graph
        self.data_dir = Path(data_dir)
        self.parser = ParquetParser(str(self.data_dir))
        self.logger = logger

    def load_cooccurrence_graph(self) -> int:
        """
        加载技能共现关系图

        Returns:
            加载的关系数量
        """
        self.logger.info("🔗 加载技能共现关系图")

        try:
            graph_df = self.parser.parse_graph_data('co_occurrence')

            relation_count = 0
            batch_size = 1000

            for idx, row in graph_df.iterrows():
                skill_id_1 = row.get('skill_id_1')
                skill_id_2 = row.get('skill_id_2')

                if skill_id_1 is None or skill_id_2 is None:
                    continue

                relation_type = 'co_occurrence'
                weight = float(row.get('frequency', row.get('weight', 1.0)))
                co_occurrence_count = int(row.get('count', weight * 100))

                if self.db.insert_skill_relation(
                    int(skill_id_1),
                    int(skill_id_2),
                    relation_type,
                    weight,
                    co_occurrence_count
                ):
                    self.graph.add_skill_relation(
                        int(skill_id_1),
                        int(skill_id_2),
                        relation_type,
                        weight,
                        {'co_occurrence_count': co_occurrence_count}
                    )
                    relation_count += 1

                if (idx + 1) % batch_size == 0:
                    self.logger.info(f"  已处理 {idx + 1} 条关系...")

            self.logger.info(f"✅ 成功加载 {relation_count} 条共现关系")
            return relation_count

        except Exception as e:
            self.logger.error(f"❌ 加载共现图失败: {e}")
            return 0

    def build_skill_graph_from_db(self) -> int:
        """
        从数据库构建内存图谱

        Returns:
            添加的节点数量
        """
        self.logger.info("🧠 从数据库构建技能图谱")

        try:
            skills = self.db.get_all_skills()
            node_count = 0

            for skill in skills:
                self.graph.add_skill_node(skill['skill_id'], skill)
                node_count += 1

            relations = self.db.get_all_relations()
            edge_count = 0

            for rel in relations:
                self.graph.add_skill_relation(
                    rel['skill_id_1'],
                    rel['skill_id_2'],
                    rel['relation_type'],
                    rel['weight'],
                    {'co_occurrence_count': rel.get('co_occurrence_count', 0)}
                )
                edge_count += 1

            self.logger.info(f"✅ 图谱构建完成: {node_count} 节点, {edge_count} 边")
            return node_count

        except Exception as e:
            self.logger.error(f"❌ 构建图谱失败: {e}")
            return 0

    def infer_skill_relations(self, min_cooccurrence: int = 10) -> int:
        """
        基于共现次数推断其他关系

        Args:
            min_cooccurrence: 最小共现次数阈值

        Returns:
            推断的关系数量
        """
        self.logger.info("🤖 基于共现推断技能关系")

        try:
            relations = self.db.get_all_relations()
            inferred_count = 0

            for rel in relations:
                if rel['relation_type'] != 'co_occurrence':
                    continue

                co_count = rel.get('co_occurrence_count', 0)

                if co_count >= min_cooccurrence:
                    skill1 = self.db.get_skill_by_id(rel['skill_id_1'])
                    skill2 = self.db.get_skill_by_id(rel['skill_id_2'])

                    if skill1 and skill2:
                        if skill1.get('category') == skill2.get('category'):
                            self.graph.add_skill_relation(
                                rel['skill_id_1'],
                                rel['skill_id_2'],
                                'same_category',
                                0.8
                            )
                            inferred_count += 1

            self.logger.info(f"✅ 推断 {inferred_count} 条同类关系")
            return inferred_count

        except Exception as e:
            self.logger.error(f"❌ 推断关系失败: {e}")
            return 0

    def save_graph_to_file(self):
        """保存图谱到文件"""
        self.logger.info("💾 保存图谱到文件")
        self.graph.save_graph()

    def load_graph_from_file(self) -> bool:
        """从文件加载图谱"""
        self.logger.info("📂 从文件加载图谱")
        return self.graph.load_graph()

    def get_graph_statistics(self) -> Dict:
        """
        获取图谱统计信息

        Returns:
            统计信息字典
        """
        stats = self.graph.get_skill_graph_stats()
        stats['db_skill_count'] = self.db.get_skill_count()
        stats['db_relation_count'] = self.db.get_relation_count()

        return stats
