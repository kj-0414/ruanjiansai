# 人才智能匹配系统 - Job-SDF 知识库构建方案

## 📋 项目概述

### 1.1 数据源分析

**Job-SDF 数据集**包含以下核心数据：

| 数据目录 | 内容描述 | 数据格式 | 规模 |
|---------|---------|---------|------|
| `demand/` | 技能月度招聘需求 | Parquet | 2324技能 × 多时间点 |
| `proportion/` | 技能需求占比 | Parquet | 同上 |
| `graph/` | 技能共现关系图 | Parquet (三元组) | 数万条边 |
| `structural_breaks_index/` | 结构突变技能索引 | JSON | 数百个技能 |
| `low_frequency_index/` | 低频技能索引 | JSON | 数千个技能 |

### 1.2 知识库目标

构建一个**职业技能知识图谱系统**，包含：
- ✅ 2324个标准技能实体
- ✅ 技能间的语义关系（共现、层级、相似）
- ✅ 职业分类体系（14个一级、52个二级）
- ✅ 时序需求趋势数据
- ✅ 技能-职业映射关系

---

## 🏗️ 整体架构设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          用户应用层                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ ResumeParse │  │  JobParse   │  │   Match    │  │   Graph    │      │
│  │   Agent     │  │   Agent     │  │   Agent    │  │   Agent    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Agent调用层                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    Knowledge Base Service (知识库服务)                   │  │
│  │  ├── 技能查询 (get_skill_info)                                        │  │
│  │  ├── 关系推理 (get_related_skills, get_skill_path)                   │  │
│  │  ├── 趋势分析 (get_skill_trend, get_demand_forecast)                   │  │
│  │  ├── 职业映射 (map_skills_to_occupation)                               │  │
│  │  └── 匹配增强 (enhance_match_with_knowledge)                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          数据存储层                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│  │  SQLite/SQLite │  │  NetworkX Graph  │  │  Pandas DataFrame│          │
│  │   (主数据库)    │  │    (图数据库)    │  │    (时序数据)    │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘           │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Neo4j/GDB (可选专业图数据库)                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          数据导入层                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    Job-SDF Data Importer                                │  │
│  │  ├── Parquet Parser (demand, proportion, graph)                       │  │
│  │  ├── JSON Parser (structural_breaks, low_frequency)                  │  │
│  │  ├── Skill Normalizer (标准化技能名称)                                  │  │
│  │  └── Graph Builder (构建技能关系图)                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ 数据库设计

### 3.1 技能主表 (skills)

```sql
CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_aliases TEXT,              -- JSON数组：["Python", "python", "py"]
    category VARCHAR(50),           -- 技能大类：编程语言、框架、数据库等
    sub_category VARCHAR(50),       -- 技能子类
    difficulty_level INTEGER,        -- 难度等级：1-5
    is_hot_skill BOOLEAN,           -- 是否热门技能
    is_structural_break BOOLEAN,    -- 是否结构突变技能
    is_low_frequency BOOLEAN,      -- 是否低频技能
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_skill_name ON skills(skill_name);
CREATE INDEX idx_category ON skills(category);
CREATE INDEX idx_is_hot ON skills(is_hot_skill);
```

### 3.2 技能关系表 (skill_relations)

```sql
CREATE TABLE skill_relations (
    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id_1 INTEGER NOT NULL,
    skill_id_2 INTEGER NOT NULL,
    relation_type VARCHAR(50) NOT NULL,  -- co_occurrence, similar, prerequisite, same_category
    weight FLOAT,                        -- 关系权重（0-1）
    co_occurrence_count INTEGER,         -- 共现次数
    co_occurrence_frequency FLOAT,       -- 共现频率
    created_at TIMESTAMP,
    FOREIGN KEY (skill_id_1) REFERENCES skills(skill_id),
    FOREIGN KEY (skill_id_2) REFERENCES skills(skill_id),
    UNIQUE(skill_id_1, skill_id_2, relation_type)
);

CREATE INDEX idx_relation_skill1 ON skill_relations(skill_id_1);
CREATE INDEX idx_relation_skill2 ON skill_relations(skill_id_2);
CREATE INDEX idx_relation_type ON skill_relations(relation_type);
```

### 3.3 职业分类表 (occupations)

```sql
CREATE TABLE occupations (
    occupation_id INTEGER PRIMARY KEY,
    level1_code VARCHAR(10),         -- 一级职业编码
    level1_name VARCHAR(100),         -- 一级职业名称
    level2_code VARCHAR(20),          -- 二级职业编码
    level2_name VARCHAR(100),        -- 二级职业名称
    description TEXT,
    key_skills TEXT,                -- JSON数组：核心技能ID列表
    optional_skills TEXT,            -- JSON数组：可选技能ID列表
    demand_level VARCHAR(20),        -- 需求级别：high, medium, low
    created_at TIMESTAMP
);

CREATE INDEX idx_level1 ON occupations(level1_code);
CREATE INDEX idx_level2 ON occupations(level2_code);
```

### 3.4 技能需求时序表 (skill_demand)

```sql
CREATE TABLE skill_demand (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    demand_value FLOAT NOT NULL,      -- 需求量
    proportion_value FLOAT,          -- 需求占比
    time_period VARCHAR(20),          -- 时间周期：YYYY-MM
    region VARCHAR(50),               -- 地区
    granularity VARCHAR(20),          -- 粒度：company, occupation, region
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
    UNIQUE(skill_id, time_period, region, granularity)
);

CREATE INDEX idx_demand_skill ON skill_demand(skill_id);
CREATE INDEX idx_demand_time ON skill_demand(time_period);
```

### 3.5 技能-职业映射表 (skill_occupation_mapping)

```sql
CREATE TABLE skill_occupation_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    occupation_id INTEGER NOT NULL,
    importance_weight FLOAT,          -- 重要性权重
    is_core_skill BOOLEAN,            -- 是否核心技能
    demand_growth_rate FLOAT,        -- 需求增长率
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
    FOREIGN KEY (occupation_id) REFERENCES occupations(occupation_id),
    UNIQUE(skill_id, occupation_id)
);
```

---

## 📊 图数据结构设计

### 4.1 使用 NetworkX 构建技能知识图谱

```python
class SkillKnowledgeGraph:
    """
    技能知识图谱 - 基于NetworkX实现
    """

    def __init__(self):
        self.graph = nx.DiGraph()  # 有向图
        self.skill_nodes = {}      # 技能节点信息
        self.occupation_nodes = {} # 职业节点信息

    def add_skill_node(self, skill_id: int, skill_info: dict):
        """添加技能节点"""
        self.graph.add_node(
            f"skill_{skill_id}",
            node_type="skill",
            **skill_info
        )

    def add_occupation_node(self, occupation_id: int, occ_info: dict):
        """添加职业节点"""
        self.graph.add_node(
            f"occupation_{occupation_id}",
            node_type="occupation",
            **occ_info
        )

    def add_skill_relation(self, skill1_id: int, skill2_id: int,
                          relation_type: str, weight: float):
        """添加技能关系"""
        self.graph.add_edge(
            f"skill_{skill1_id}",
            f"skill_{skill2_id}",
            relation_type=relation_type,
            weight=weight
        )

    def add_skill_to_occupation(self, skill_id: int, occupation_id: int,
                               importance: float):
        """添加技能-职业关联"""
        self.graph.add_edge(
            f"skill_{skill_id}",
            f"occupation_{occupation_id}",
            relation_type="required_for",
            importance=importance
        )

    def get_related_skills(self, skill_id: int, max_depth: int = 2) -> List[dict]:
        """获取相关技能（基于图遍历）"""
        node = f"skill_{skill_id}"
        related = []

        # BFS遍历
        for neighbor in nx.single_source_shortest_path_length(
            self.graph, node, cutoff=max_depth
        ).keys():
            if neighbor.startswith("skill_"):
                related.append({
                    "skill_id": int(neighbor.split("_")[1]),
                    "distance": nx.shortest_path_length(self.graph, node, neighbor),
                    **self.graph.nodes[neighbor]
                })

        return related

    def get_skill_learning_path(self, from_skill: int, to_skill: int) -> List[dict]:
        """获取技能学习路径"""
        path = nx.shortest_path(
            self.graph,
            f"skill_{from_skill}",
            f"skill_{to_skill}"
        )

        return [
            {
                "node": node,
                "node_type": self.graph.nodes[node].get("node_type"),
                **self.graph.nodes[node]
            }
            for node in path
        ]
```

---

## 🔄 数据导入流程

### 5.1 数据导入脚本架构

```
scripts/
├── import_job_sdf.py              # 主导入脚本
├── parsers/
│   ├── __init__.py
│   ├── parquet_parser.py          # Parquet文件解析
│   ├── json_parser.py             # JSON文件解析
│   └── data_normalizer.py         # 数据标准化
├── loaders/
│   ├── __init__.py
│   ├── skill_loader.py            # 技能数据加载
│   ├── graph_loader.py            # 图数据加载
│   ├── timeseries_loader.py       # 时序数据加载
│   └── occupation_loader.py        # 职业数据加载
└── utils/
    ├── __init__.py
    ├── db_connection.py           # 数据库连接
    └── logger.py                  # 日志工具
```

### 5.2 主导入脚本

```python
#!/usr/bin/env python3
"""
Job-SDF 数据集导入脚本
将数据集导入到人才匹配系统的知识库中
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.knowledge_base.db import KnowledgeBaseDB
from modules.knowledge_base.graph import SkillKnowledgeGraph
from modules.knowledge_base.loaders import (
    SkillLoader,
    GraphLoader,
    TimeSeriesLoader,
    OccupationLoader
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobSDFImporter:
    """Job-SDF数据集导入器"""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.db = KnowledgeBaseDB()
        self.graph = SkillKnowledgeGraph()
        self.logger = logger

    def import_all(self):
        """执行完整导入流程"""
        self.logger.info("=" * 60)
        self.logger.info("开始导入 Job-SDF 数据集")
        self.logger.info("=" * 60)

        try:
            # 步骤1：解析和加载技能基础数据
            self._import_skills()

            # 步骤2：加载技能共现图
            self._import_skill_graph()

            # 步骤3：加载需求时序数据
            self._import_demand_timeseries()

            # 步骤4：加载职业分类数据
            self._import_occupations()

            # 步骤5：构建技能-职业映射
            self._build_skill_occupation_mapping()

            # 步骤6：构建知识图谱
            self._build_knowledge_graph()

            # 步骤7：保存图谱到文件
            self._save_graph()

            self.logger.info("=" * 60)
            self.logger.info("✅ 数据导入完成！")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"❌ 导入失败: {str(e)}")
            raise

    def _import_skills(self):
        """步骤1：从demand数据提取技能列表"""
        self.logger.info("📦 步骤1: 导入技能基础数据...")

        demand_dir = self.data_dir / "demand"
        if not demand_dir.exists():
            raise FileNotFoundError(f"需求目录不存在: {demand_dir}")

        # 读取所有parquet文件获取技能列表
        all_skills = set()
        for parquet_file in demand_dir.glob("*.parquet"):
            df = pd.read_parquet(parquet_file)
            # 假设技能名称在索引或列名中
            if df.index.name == 'skill_id' or 'skill_id' in df.columns:
                skill_col = 'skill_id' if 'skill_id' in df.columns else df.index
                all_skills.update(skill_col.tolist())

        self.logger.info(f"  发现 {len(all_skills)} 个技能")

        # 从structural_breaks和low_frequency加载技能信息
        breaks_dir = self.data_dir / "structural_breaks_index"
        low_freq_dir = self.data_dir / "low_frequency_index"

        skill_info = {}
        for skill_id in all_skills:
            skill_info[skill_id] = {
                'skill_name': f"skill_{skill_id}",
                'aliases': [],
                'category': self._infer_category(skill_id),
                'difficulty_level': 3,
                'is_structural_break': skill_id in self._load_breaks_index(breaks_dir),
                'is_low_frequency': skill_id in self._load_low_freq_index(low_freq_dir)
            }

        # 插入数据库
        for skill_id, info in skill_info.items():
            self.db.insert_skill(skill_id, info)

        self.logger.info(f"  ✅ 成功导入 {len(skill_info)} 个技能")

    def _import_skill_graph(self):
        """步骤2：从graph数据加载技能关系"""
        self.logger.info("🔗 步骤2: 导入技能关系图...")

        graph_dir = self.data_dir / "graph"
        if not graph_dir.exists():
            self.logger.warning(f"  ⚠️ 图数据目录不存在: {graph_dir}")
            return

        for graph_file in graph_dir.glob("*.parquet"):
            df = pd.read_parquet(graph_file)
            # 假设格式：skill_id_1, skill_id_2, frequency
            for _, row in df.iterrows():
                self.db.insert_skill_relation(
                    row['skill_id_1'],
                    row['skill_id_2'],
                    'co_occurrence',
                    row.get('frequency', 1)
                )

        self.logger.info(f"  ✅ 技能关系图导入完成")

    def _import_demand_timeseries(self):
        """步骤3：从demand数据加载时序需求"""
        self.logger.info("📈 步骤3: 导入需求时序数据...")

        demand_dir = self.data_dir / "demand"
        proportion_dir = self.data_dir / "proportion"

        for demand_file in demand_dir.glob("*.parquet"):
            df = pd.read_parquet(demand_file)

            # 获取时间列（假设是月份格式）
            time_columns = [col for col in df.columns if self._is_time_column(col)]

            for skill_id, row in df.iterrows():
                for time_col in time_columns:
                    self.db.insert_skill_demand(
                        skill_id,
                        row[time_col],
                        self._get_proportion(skill_id, time_col, proportion_dir),
                        time_col
                    )

        self.logger.info(f"  ✅ 需求时序数据导入完成")

    def _import_occupations(self):
        """步骤4：导入职业分类数据"""
        self.logger.info("💼 步骤4: 导入职业分类...")

        # Job-SDF包含14个一级职业、52个二级职业
        occupations = [
            {"level1_code": "L1-01", "level1_name": "计算机软件", "level2_code": "L2-0101", "level2_name": "前端开发"},
            {"level1_code": "L1-01", "level1_name": "计算机软件", "level2_code": "L2-0102", "level2_name": "后端开发"},
            {"level1_code": "L1-01", "level1_name": "计算机软件", "level2_code": "L2-0103", "level2_name": "全栈开发"},
            # ... 其他职业
        ]

        for occ in occupations:
            self.db.insert_occupation(occ)

        self.logger.info(f"  ✅ 成功导入 {len(occupations)} 个职业分类")

    def _build_skill_occupation_mapping(self):
        """步骤5：构建技能-职业映射"""
        self.logger.info("🗺️ 步骤5: 构建技能-职业映射...")

        # 基于技能共现关系推断映射
        # 或者使用外部提供的映射数据
        pass

    def _build_knowledge_graph(self):
        """步骤6：在内存中构建完整知识图谱"""
        self.logger.info("🧠 步骤6: 构建知识图谱...")

        # 加载所有技能节点
        skills = self.db.get_all_skills()
        for skill in skills:
            self.graph.add_skill_node(skill['skill_id'], skill)

        # 加载所有技能关系
        relations = self.db.get_all_relations()
        for rel in relations:
            self.graph.add_skill_relation(
                rel['skill_id_1'],
                rel['skill_id_2'],
                rel['relation_type'],
                rel['weight']
            )

        self.logger.info(f"  图谱节点数: {self.graph.graph.number_of_nodes()}")
        self.logger.info(f"  图谱边数: {self.graph.graph.number_of_edges()}")
        self.logger.info(f"  ✅ 知识图谱构建完成")

    def _save_graph(self):
        """步骤7：保存图谱到文件"""
        self.logger.info("💾 步骤7: 保存图谱...")

        graph_path = Path(__file__).parent.parent / "modules" / "knowledge_base" / "data"
        graph_path.mkdir(parents=True, exist_ok=True)

        # 保存为NetworkX格式
        nx.write_gpickle(self.graph.graph, graph_path / "skill_graph.gpickle")

        # 保存节点和边信息
        with open(graph_path / "graph_info.json", "w", encoding="utf-8") as f:
            json.dump({
                "node_count": self.graph.graph.number_of_nodes(),
                "edge_count": self.graph.graph.number_of_edges(),
                "last_updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        self.logger.info(f"  ✅ 图谱已保存到: {graph_path}")


def main():
    """主函数"""
    # 数据集路径
    data_dir = Path(__file__).parent.parent.parent.parent / "benchmark-main" / "dataset"

    if not data_dir.exists():
        print(f"❌ 数据集目录不存在: {data_dir}")
        print("请先下载 Job-SDF 数据集")
        sys.exit(1)

    importer = JobSDFImporter(str(data_dir))
    importer.import_all()


if __name__ == "__main__":
    main()
```

---

## 🚀 Agent集成方案

### 6.1 知识库服务接口

```python
# modules/knowledge_base/service.py

class KnowledgeBaseService:
    """知识库服务 - 被Agent调用"""

    def __init__(self):
        self.db = KnowledgeBaseDB()
        self.graph = self._load_graph()

    def get_skill_info(self, skill_name: str) -> dict:
        """获取技能详细信息"""
        skill = self.db.get_skill_by_name(skill_name)
        if not skill:
            return None

        # 补充关系信息
        relations = self.db.get_skill_relations(skill['skill_id'])
        skill['relations'] = relations

        return skill

    def normalize_skill(self, raw_skill_name: str) -> dict:
        """标准化技能名称"""
        # 1. 精确匹配
        skill = self.db.get_skill_by_name(raw_skill_name)
        if skill:
            return {'normalized': skill['skill_name'], 'confidence': 1.0, 'skill_id': skill['skill_id']}

        # 2. 别名匹配
        skill = self.db.get_skill_by_alias(raw_skill_name)
        if skill:
            return {'normalized': skill['skill_name'], 'confidence': 0.95, 'skill_id': skill['skill_id']}

        # 3. 模糊匹配（基于相似度）
        similar = self._fuzzy_match_skill(raw_skill_name)
        if similar:
            return {'normalized': similar['skill_name'], 'confidence': similar['similarity'], 'skill_id': similar['skill_id']}

        # 4. 未找到
        return {'normalized': raw_skill_name, 'confidence': 0, 'skill_id': None}

    def get_related_skills(self, skill_id: int, max_count: int = 10) -> List[dict]:
        """获取相关技能"""
        # 使用图数据库查询
        related = self.graph.get_related_skills(skill_id, max_depth=2)

        # 按权重排序
        related.sort(key=lambda x: x.get('weight', 0), reverse=True)

        return related[:max_count]

    def enhance_match(self, resume_skills: List[str], job_skills: List[str]) -> dict:
        """增强匹配 - 利用知识库"""
        # 1. 标准化所有技能
        resume_normalized = [self.normalize_skill(s) for s in resume_skills]
        job_normalized = [self.normalize_skill(s) for s in job_skills]

        # 2. 直接匹配
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
                        'match_type': 'direct',
                        'confidence': 1.0
                    })
                    matched = True
                    break

            if not matched:
                missing_skills.append(job_skill)

        # 3. 相关技能匹配
        related_matches = []
        for missing in missing_skills:
            related = self.get_related_skills(missing['skill_id'], max_count=5)

            # 检查是否有简历中的相关技能
            for rel_skill in related:
                for resume_skill in resume_normalized:
                    if resume_skill['skill_id'] == rel_skill['skill_id']:
                        related_matches.append({
                            'job_skill': missing['normalized'],
                            'resume_skill': resume_skill['normalized'],
                            'relation': rel_skill.get('relation_type', 'similar'),
                            'confidence': rel_skill.get('weight', 0.5)
                        })
                        break

        # 4. 计算增强分数
        direct_score = len(direct_matches) / len(job_normalized) if job_normalized else 0
        related_score = len(related_matches) / len(missing_skills) if missing_skills else 0
        enhanced_score = direct_score * 0.8 + related_score * 0.2

        return {
            'direct_matches': direct_matches,
            'related_matches': related_matches,
            'missing_skills': missing_skills,
            'direct_score': direct_score,
            'related_score': related_score,
            'enhanced_score': enhanced_score
        }
```

### 6.2 Agent集成示例

```python
# modules/agents/resume_agent.py (增强版)

from modules.knowledge_base.service import KnowledgeBaseService

class ResumeParseAgent:
    def __init__(self):
        self.qwen_client = get_qwen_client()
        self.knowledge_base = KnowledgeBaseService()

    def _extract_skills_from_text(self, text: str) -> List[dict]:
        """增强版技能提取 - 使用知识库"""
        # 1. AI提取原始技能列表
        ai_skills = self._extract_skills_ai(text)

        # 2. 标准化并验证每个技能
        validated_skills = []
        for skill_name in ai_skills:
            result = self.knowledge_base.normalize_skill(skill_name)
            if result['confidence'] > 0.5:
                validated_skills.append({
                    'original': skill_name,
                    'normalized': result['normalized'],
                    'skill_id': result['skill_id'],
                    'confidence': result['confidence'],
                    'related_skills': self.knowledge_base.get_related_skills(result['skill_id'], max_count=3)
                })

        return validated_skills
```

---

## 📅 实施计划

### 阶段1：数据层构建（1-2周）
- [ ] 设计并创建数据库表结构
- [ ] 实现Parquet和JSON解析器
- [ ] 完成数据导入脚本
- [ ] 验证数据完整性

### 阶段2：知识图谱构建（1周）
- [ ] 实现SkillKnowledgeGraph类
- [ ] 构建技能关系图
- [ ] 实现图查询算法
- [ ] 优化查询性能

### 阶段3：服务层开发（1周）
- [ ] 实现KnowledgeBaseService
- [ ] 开发RESTful API接口
- [ ] 实现缓存机制
- [ ] 编写单元测试

### 阶段4：Agent集成（1-2周）
- [ ] 集成到ResumeParseAgent
- [ ] 集成到JobParseAgent
- [ ] 集成到MatchAgent
- [ ] 集成到GraphAgent
- [ ] 端到端测试

### 阶段5：优化与上线（1周）
- [ ] 性能优化
- [ ] 错误处理完善
- [ ] 文档编写
- [ ] 部署上线

---

## 📁 文件结构

```
talent-match-system/
└── backend/
    └── modules/
        └── knowledge_base/
            ├── __init__.py
            ├── db.py                    # 数据库操作
            ├── graph.py                 # 图数据结构
            ├── service.py               # 知识库服务
            ├── normalizer.py            # 数据标准化
            ├── parsers/
            │   ├── __init__.py
            │   ├── parquet_parser.py
            │   └── json_parser.py
            ├── loaders/
            │   ├── __init__.py
            │   ├── skill_loader.py
            │   ├── graph_loader.py
            │   └── timeseries_loader.py
            └── data/
                ├── skill_graph.gpickle
                ├── graph_info.json
                └── cache/
```

---

## ✅ 验收标准

1. **数据完整性**：成功导入所有数据集
2. **查询性能**：单次查询 < 100ms
3. **匹配增强**：技能匹配覆盖率提升 ≥ 30%
4. **Agent集成**：所有Agent成功调用知识库
5. **代码质量**：通过单元测试，无致命错误

---

**文档版本**: v1.0
**创建日期**: 2026-05-23
**维护人**: AI Assistant
