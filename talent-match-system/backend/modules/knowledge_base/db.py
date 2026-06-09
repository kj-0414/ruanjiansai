"""
知识库数据库操作模块
负责与SQLite数据库交互
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class KnowledgeBaseDB:
    """知识库数据库管理类"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_dir = Path(__file__).parent / "data"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "knowledge_base.db")

        self.db_path = db_path
        self.conn = None
        self._connect()
        self._init_tables()
        self._load_standard_skills()  # 加载标准技能数据

    def _connect(self):
        """建立数据库连接"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"✅ 已连接到知识库数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise

    def _init_tables(self):
        """初始化数据库表结构"""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY,
                skill_name TEXT NOT NULL UNIQUE,
                skill_aliases TEXT,
                category TEXT,
                sub_category TEXT,
                difficulty_level INTEGER DEFAULT 3,
                is_hot_skill INTEGER DEFAULT 0,
                is_structural_break INTEGER DEFAULT 0,
                is_low_frequency INTEGER DEFAULT 0,
                description TEXT,
                demand_weight REAL DEFAULT 0.0,
                avg_demand REAL DEFAULT 0.0,
                total_demand REAL DEFAULT 0.0,
                demand_trend REAL DEFAULT 0.0,
                cooccurrence_count INTEGER DEFAULT 0,
                source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_name ON skills(skill_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON skills(category)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_relations (
                relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id_1 INTEGER NOT NULL,
                skill_id_2 INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                co_occurrence_count INTEGER DEFAULT 0,
                co_occurrence_frequency REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (skill_id_1) REFERENCES skills(skill_id),
                FOREIGN KEY (skill_id_2) REFERENCES skills(skill_id),
                UNIQUE(skill_id_1, skill_id_2, relation_type)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relation_skill1 ON skill_relations(skill_id_1)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relation_skill2 ON skill_relations(skill_id_2)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS occupations (
                occupation_id INTEGER PRIMARY KEY,
                level1_code TEXT,
                level1_name TEXT,
                level2_code TEXT,
                level2_name TEXT NOT NULL,
                description TEXT,
                key_skills TEXT,
                optional_skills TEXT,
                demand_level TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_demand (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER NOT NULL,
                demand_value REAL NOT NULL,
                proportion_value REAL,
                time_period TEXT NOT NULL,
                region TEXT DEFAULT 'global',
                granularity TEXT DEFAULT 'global',
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
                UNIQUE(skill_id, time_period, region, granularity)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_demand_skill ON skill_demand(skill_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_demand_time ON skill_demand(time_period)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_occupation_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER NOT NULL,
                occupation_id INTEGER NOT NULL,
                importance_weight REAL DEFAULT 0.5,
                is_core_skill INTEGER DEFAULT 0,
                demand_growth_rate REAL DEFAULT 0.0,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
                FOREIGN KEY (occupation_id) REFERENCES occupations(occupation_id),
                UNIQUE(skill_id, occupation_id)
            )
        """)

        self.conn.commit()
        logger.info("✅ 数据库表初始化完成")

    def insert_skill(self, skill_id: int, skill_info: Dict) -> bool:
        """插入技能记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO skills
                (skill_id, skill_name, skill_aliases, category, difficulty_level,
                 is_hot_skill, is_structural_break, is_low_frequency, description, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill_id,
                skill_info.get('skill_name', f'skill_{skill_id}'),
                json.dumps(skill_info.get('aliases', []), ensure_ascii=False),
                skill_info.get('category'),
                skill_info.get('difficulty_level', 3),
                1 if skill_info.get('is_hot_skill') else 0,
                1 if skill_info.get('is_structural_break') else 0,
                1 if skill_info.get('is_low_frequency') else 0,
                skill_info.get('description'),
                datetime.now()
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ 插入技能失败: {e}")
            return False

    def get_skill_by_id(self, skill_id: int) -> Optional[Dict]:
        """根据ID获取技能"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM skills WHERE skill_id = ?", (skill_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_skill_by_name(self, skill_name: str) -> Optional[Dict]:
        """根据名称获取技能（精确匹配）"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM skills WHERE LOWER(skill_name) = LOWER(?)",
            (skill_name,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_skill_by_alias(self, alias: str) -> Optional[Dict]:
        """根据别名获取技能"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM skills WHERE skill_aliases LIKE ?", (f'%"{alias}"%',))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_skills(self) -> List[Dict]:
        """获取所有技能"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM skills ORDER BY skill_id")
        return [dict(row) for row in cursor.fetchall()]

    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """
        根据技能名称获取技能信息（包含所有增强字段）
        """
        cursor = self.conn.cursor()
        # 尝试精确匹配
        cursor.execute(
            "SELECT * FROM skills WHERE LOWER(skill_name) = LOWER(?)",
            (skill_name,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        # 尝试别名匹配
        cursor.execute(
            "SELECT * FROM skills WHERE skill_aliases LIKE ?",
            (f'%"{skill_name}"%',)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def insert_skill_relation(self, skill_id_1: int, skill_id_2: int,
                             relation_type: str, weight: float = 1.0,
                             co_occurrence_count: int = 0) -> bool:
        """插入技能关系"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO skill_relations
                (skill_id_1, skill_id_2, relation_type, weight, co_occurrence_count,
                 co_occurrence_frequency, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                skill_id_1, skill_id_2, relation_type, weight,
                co_occurrence_count,
                co_occurrence_count / 1000.0 if co_occurrence_count else 0.0
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ 插入技能关系失败: {e}")
            return False

    def get_skill_relations(self, skill_identifier: Optional[int] = None,
                          relation_type: Optional[str] = None,
                          skill_name: Optional[str] = None) -> List[Dict]:
        """获取技能的所有关系"""
        skill_id = skill_identifier
        
        # 如果提供了 skill_name，则先查找对应的 skill_id
        if skill_name:
            skill = self.get_skill_by_name(skill_name)
            if skill:
                skill_id = skill['skill_id']
            else:
                return []
        
        if not skill_id:
            return []
        
        cursor = self.conn.cursor()
        if relation_type:
            cursor.execute("""
                SELECT * FROM skill_relations
                WHERE skill_id_1 = ? AND relation_type = ?
                ORDER BY weight DESC
            """, (skill_id, relation_type))
        else:
            cursor.execute("""
                SELECT * FROM skill_relations
                WHERE skill_id_1 = ? OR skill_id_2 = ?
                ORDER BY weight DESC
            """, (skill_id, skill_id))
        
        relations = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            # 转换为更容易理解的格式
            target_skill_id = row_dict['skill_id_2'] if row_dict['skill_id_1'] == skill_id else row_dict['skill_id_1']
            target_skill = self.get_skill_by_id(target_skill_id)
            if target_skill:
                row_dict['target_skill'] = target_skill['skill_name']
            relations.append(row_dict)

        return relations

    def get_all_relations(self) -> List[Dict]:
        """获取所有技能关系"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM skill_relations")
        return [dict(row) for row in cursor.fetchall()]

    def insert_occupation(self, occupation_info: Dict) -> bool:
        """插入职业分类"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO occupations
                (level1_code, level1_name, level2_code, level2_name,
                 description, key_skills, optional_skills, demand_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                occupation_info.get('level1_code'),
                occupation_info.get('level1_name'),
                occupation_info.get('level2_code'),
                occupation_info.get('level2_name'),
                occupation_info.get('description'),
                json.dumps(occupation_info.get('key_skills', []), ensure_ascii=False),
                json.dumps(occupation_info.get('optional_skills', []), ensure_ascii=False),
                occupation_info.get('demand_level', 'medium')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ 插入职业分类失败: {e}")
            return False

    def get_occupation_by_id(self, occupation_id: int) -> Optional[Dict]:
        """根据ID获取职业"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM occupations WHERE occupation_id = ?", (occupation_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def insert_skill_demand(self, skill_id: int, demand_value: float,
                           proportion_value: Optional[float],
                           time_period: str,
                           region: str = 'global',
                           granularity: str = 'global') -> bool:
        """插入技能需求数据"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO skill_demand
                (skill_id, demand_value, proportion_value, time_period, region, granularity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (skill_id, demand_value, proportion_value, time_period, region, granularity))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ 插入需求数据失败: {e}")
            return False

    def get_skill_demand_trend(self, skill_id: int,
                              start_period: Optional[str] = None,
                              end_period: Optional[str] = None) -> List[Dict]:
        """获取技能需求趋势"""
        cursor = self.conn.cursor()
        if start_period and end_period:
            cursor.execute("""
                SELECT * FROM skill_demand
                WHERE skill_id = ? AND time_period BETWEEN ? AND ?
                ORDER BY time_period
            """, (skill_id, start_period, end_period))
        else:
            cursor.execute("""
                SELECT * FROM skill_demand
                WHERE skill_id = ?
                ORDER BY time_period
            """, (skill_id,))

        return [dict(row) for row in cursor.fetchall()]

    def search_skills(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索技能（模糊匹配）"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM skills
            WHERE skill_name LIKE ? OR skill_aliases LIKE ?
            LIMIT ?
        """, (f'%{keyword}%', f'%"{keyword}"%', limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_hot_skills(self, limit: int = 50) -> List[Dict]:
        """获取热门技能"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.*, COUNT(sr.skill_id_1) as relation_count
            FROM skills s
            LEFT JOIN skill_relations sr ON s.skill_id = sr.skill_id_1
            WHERE s.is_hot_skill = 1
            GROUP BY s.skill_id
            ORDER BY relation_count DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_skill_count(self) -> int:
        """获取技能总数"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM skills")
        return cursor.fetchone()['count']

    def get_relation_count(self) -> int:
        """获取关系总数"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM skill_relations")
        return cursor.fetchone()['count']

    def _load_standard_skills(self):
        """加载标准技能数据"""
        try:
            from .standard_skills_data import STANDARD_SKILLS
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM skills")
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info("📦 加载标准技能数据...")
                for skill_id, skill_info in STANDARD_SKILLS.items():
                    self.insert_skill(skill_id, {
                        'skill_name': skill_info['name'],
                        'aliases': skill_info.get('aliases', []),
                        'category': skill_info['category'],
                        'difficulty_level': skill_info.get('difficulty', 3),
                        'is_hot_skill': True,
                        'is_structural_break': False,
                        'is_low_frequency': False,
                        'description': f"{skill_info['category']}: {skill_info['name']}"
                    })
                logger.info(f"✅ 已加载 {len(STANDARD_SKILLS)} 个标准技能")
            else:
                logger.info(f"ℹ️ 知识库已有 {count} 个技能，跳过加载标准技能数据")
                
        except ImportError:
            logger.warning("⚠️ 无法导入标准技能数据模块")
        except Exception as e:
            logger.error(f"❌ 加载标准技能数据失败: {e}")

    def get_skill_by_name_or_alias(self, name: str) -> Optional[Dict]:
        """根据名称或别名获取技能（增强版）"""
        skill = self.get_skill_by_name(name)
        if skill:
            return skill
        
        skill = self.get_skill_by_alias(name)
        return skill

    def fuzzy_match_skill(self, text: str, threshold: float = 0.6) -> List[Dict]:
        """模糊匹配技能"""
        all_skills = self.get_all_skills()
        matches = []
        
        text_lower = text.lower().strip()
        
        for skill in all_skills:
            skill_name_lower = skill['skill_name'].lower()
            
            if text_lower in skill_name_lower or skill_name_lower in text_lower:
                matches.append({
                    **skill,
                    'similarity': 1.0 if text_lower == skill_name_lower else 0.8
                })
                continue
            
            aliases_text = skill.get('skill_aliases', '[]')
            try:
                aliases = json.loads(aliases_text)
                for alias in aliases:
                    if text_lower == alias.lower():
                        matches.append({
                            **skill,
                            'similarity': 1.0
                        })
                        break
            except:
                pass
        
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches[:10]

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("✅ 数据库连接已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
