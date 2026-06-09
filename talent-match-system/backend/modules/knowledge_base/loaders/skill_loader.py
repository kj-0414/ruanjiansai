"""
技能数据加载器
将技能数据加载到知识库数据库
"""

import logging
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path

from ..db import KnowledgeBaseDB
from ..parsers import ParquetParser, JSONParser, DataNormalizer

logger = logging.getLogger(__name__)


class SkillLoader:
    """技能数据加载器"""

    def __init__(self, db: KnowledgeBaseDB, data_dir: str):
        self.db = db
        self.data_dir = Path(data_dir)
        self.parser = ParquetParser(str(self.data_dir))
        self.json_parser = JSONParser(str(self.data_dir))
        self.normalizer = DataNormalizer()
        self.logger = logger

    def load_skills_from_demand(self, granularity: str = 'global') -> int:
        """
        从需求数据加载技能列表

        Args:
            granularity: 数据粒度

        Returns:
            加载的技能数量
        """
        self.logger.info(f"📦 从需求数据加载技能 (粒度: {granularity})")

        try:
            demand_df = self.parser.parse_demand_data(granularity)
            skill_ids = self.parser.get_skill_ids_from_dataframe(demand_df)

            structural_breaks = set(self.json_parser.parse_structural_breaks())
            low_frequency = set(self.json_parser.parse_low_frequency())

            loaded_count = 0
            for skill_id in skill_ids:
                skill_info = {
                    'skill_name': f'skill_{skill_id}',
                    'aliases': [],
                    'category': '其他',
                    'difficulty_level': 3,
                    'is_hot_skill': skill_id not in low_frequency,
                    'is_structural_break': str(skill_id) in structural_breaks,
                    'is_low_frequency': str(skill_id) in low_frequency
                }

                if self.db.insert_skill(skill_id, skill_info):
                    loaded_count += 1

            self.logger.info(f"✅ 成功加载 {loaded_count} 个技能")
            return loaded_count

        except Exception as e:
            self.logger.error(f"❌ 加载技能失败: {e}")
            return 0

    def load_skill_aliases(self) -> int:
        """
        加载技能别名映射

        Returns:
            更新的技能数量
        """
        self.logger.info("🔄 加载技能别名映射")

        try:
            aliases = self.json_parser.parse_skill_aliases()
            updated_count = 0

            for skill_name, alias_list in aliases.items():
                normalized_name = self.normalizer.normalize_skill_name(skill_name)
                skill = self.db.get_skill_by_name(normalized_name)

                if skill:
                    skill['skill_aliases'] = alias_list
                    skill['category'] = self.normalizer.detect_category(normalized_name)
                    self.db.insert_skill(skill['skill_id'], skill)
                    updated_count += 1
                else:
                    new_skill_id = hash(normalized_name) % 100000
                    skill_info = {
                        'skill_name': normalized_name,
                        'aliases': alias_list,
                        'category': self.normalizer.detect_category(normalized_name),
                        'difficulty_level': 3,
                        'is_hot_skill': True
                    }
                    self.db.insert_skill(new_skill_id, skill_info)
                    updated_count += 1

            self.logger.info(f"✅ 更新了 {updated_count} 个技能的别名")
            return updated_count

        except Exception as e:
            self.logger.error(f"❌ 加载别名失败: {e}")
            return 0

    def enrich_skill_categories(self) -> int:
        """
        丰富技能分类信息

        Returns:
            更新的技能数量
        """
        self.logger.info("📂 丰富技能分类信息")

        skills = self.db.get_all_skills()
        updated_count = 0

        for skill in skills:
            skill_name = skill.get('skill_name', '')

            category = self.normalizer.detect_category(skill_name)

            if category != '其他':
                skill['category'] = category
                self.db.insert_skill(skill['skill_id'], skill)
                updated_count += 1

        self.logger.info(f"✅ 丰富了 {updated_count} 个技能的分类")
        return updated_count

    def load_all_skills(self) -> Dict[str, int]:
        """
        加载所有技能数据

        Returns:
            加载统计信息
        """
        stats = {
            'skills_from_demand': 0,
            'skills_with_aliases': 0,
            'skills_with_categories': 0
        }

        stats['skills_from_demand'] = self.load_skills_from_demand()
        stats['skills_with_aliases'] = self.load_skill_aliases()
        stats['skills_with_categories'] = self.enrich_skill_categories()

        total_skills = self.db.get_skill_count()
        self.logger.info(f"📊 知识库中共有 {total_skills} 个技能")

        return stats
