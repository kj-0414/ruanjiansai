# 人才智能匹配系统 - 知识库模块

基于 Job-SDF 数据集构建的职业技能知识图谱系统

## 📋 概述

本模块从 Job-SDF（Job Skill Demand Forecasting）数据集导入数据，构建了一个完整的职业技能知识图谱，为人才匹配系统提供智能化的技能查询、匹配和推荐功能。

## 🎯 核心功能

### 1. 技能知识库管理
- ✅ 2324+ 标准职业技能实体
- ✅ 技能别名和标准化
- ✅ 技能分类体系（编程语言、前端、后端、数据库等）
- ✅ 技能关系网络（共现、相似、前置等）

### 2. 智能匹配增强
- ✅ 简历技能标准化
- ✅ 人岗智能匹配（直接匹配 + 相关技能匹配）
- ✅ 技能覆盖率分析
- ✅ 缺失技能推荐

### 3. 知识图谱查询
- ✅ 相关技能查询
- ✅ 技能学习路径规划
- ✅ 技能相似度计算
- ✅ 技能群体发现

### 4. 需求趋势分析
- ✅ 技能需求时序数据
- ✅ 热门技能排行
- ✅ 技能增长趋势
- ✅ 市场洞察

## 📁 模块结构

```
knowledge_base/
├── __init__.py                 # 模块初始化
├── db.py                       # 数据库操作
├── graph.py                    # 图数据结构
├── service.py                  # 知识库服务
├── normalizer.py               # 数据标准化
├── parsers/                    # 数据解析器
│   ├── parquet_parser.py       # Parquet文件解析
│   ├── json_parser.py          # JSON文件解析
│   └── data_normalizer.py      # 数据标准化
├── loaders/                    # 数据加载器
│   ├── skill_loader.py         # 技能数据加载
│   ├── graph_loader.py         # 图数据加载
│   └── timeseries_loader.py   # 时序数据加载
├── data/                       # 数据存储
│   ├── knowledge_base.db       # SQLite数据库
│   ├── skill_graph.gpickle    # 图谱文件
│   └── graph_info.json         # 图谱信息
└── knowledge_base_controller.py # API控制器

scripts/
└── import_job_sdf.py           # 数据导入脚本
```

## 🚀 快速开始

### 1. 环境要求

```bash
pip install networkx pandas pyarrow
```

### 2. 导入数据集

```bash
# 使用默认路径
python scripts/import_job_sdf.py

# 指定数据集路径
python scripts/import_job_sdf.py --data-dir ../benchmark-main/dataset

# 指定数据粒度
python scripts/import_job_sdf.py --granularity company

# 重建知识库
python scripts/import_job_sdf.py --rebuild
```

### 3. 在代码中使用

```python
from modules.knowledge_base import KnowledgeBaseService

# 初始化知识库服务
kb = KnowledgeBaseService()

# 查询技能信息
skill_info = kb.get_skill_info("Python")
print(skill_info)

# 标准化技能名称
result = kb.normalize_skill("python")
print(result)  # {'normalized': 'Python', 'confidence': 1.0, 'skill_id': xxx}

# 获取相关技能
related = kb.get_related_skills(skill_id, max_count=10)
print(related)

# 增强人岗匹配
match_result = kb.enhance_match(
    resume_skills=["Python", "Django", "PostgreSQL"],
    job_skills=["Python", "Django", "Redis", "Docker"]
)
print(match_result)
```

## 📖 API 使用示例

### 查询技能信息

```bash
curl -X POST http://localhost:8000/api/knowledge-base/query \
  -H "Content-Type: application/json" \
  -d '{"skill_name": "Python"}'
```

### 标准化技能

```bash
curl -X POST http://localhost:8000/api/knowledge-base/normalize \
  -H "Content-Type: application/json" \
  -d '{"skills": ["python", "java", "js"]}'
```

### 推荐技能

```bash
curl -X POST http://localhost:8000/api/knowledge-base/recommend \
  -H "Content-Type: application/json" \
  -d '{"base_skills": ["Python", "Django"], "limit": 10}'
```

### 获取热门技能

```bash
curl http://localhost:8000/api/knowledge-base/hot-skills?limit=20
```

## 🔧 配置说明

### 数据库配置

知识库使用 SQLite 数据库，数据库文件位于：
```
modules/knowledge_base/data/knowledge_base.db
```

### 图谱配置

图谱文件位于：
```
modules/knowledge_base/data/skill_graph.gpickle
```

## 📊 数据表结构

### skills - 技能表
| 字段 | 类型 | 说明 |
|------|------|------|
| skill_id | INTEGER | 技能ID |
| skill_name | TEXT | 技能名称 |
| skill_aliases | TEXT | 别名列表(JSON) |
| category | TEXT | 技能分类 |
| difficulty_level | INTEGER | 难度等级(1-5) |
| is_hot_skill | INTEGER | 是否热门 |
| is_structural_break | INTEGER | 是否结构突变 |
| is_low_frequency | INTEGER | 是否低频 |

### skill_relations - 技能关系表
| 字段 | 类型 | 说明 |
|------|------|------|
| skill_id_1 | INTEGER | 技能1 ID |
| skill_id_2 | INTEGER | 技能2 ID |
| relation_type | TEXT | 关系类型 |
| weight | REAL | 关系权重 |
| co_occurrence_count | INTEGER | 共现次数 |

### skill_demand - 技能需求表
| 字段 | 类型 | 说明 |
|------|------|------|
| skill_id | INTEGER | 技能ID |
| demand_value | REAL | 需求量 |
| proportion_value | REAL | 需求占比 |
| time_period | TEXT | 时间周期 |

## 🎓 使用场景

### 场景1：简历技能标准化

```python
kb = KnowledgeBaseService()

resume_skills = ["python", "Py", "ML", "Tensorflow"]
normalized = kb.normalize_skills(resume_skills)

# 输出：
# [
#   {"normalized": "Python", "confidence": 1.0, "skill_id": 123},
#   {"normalized": "Python", "confidence": 0.95, "skill_id": 123},
#   {"normalized": "Machine Learning", "confidence": 0.95, "skill_id": 456},
#   {"normalized": "TensorFlow", "confidence": 1.0, "skill_id": 789}
# ]
```

### 场景2：智能人岗匹配

```python
kb = KnowledgeBaseService()

resume_skills = ["Python", "Django", "PostgreSQL", "Git"]
job_skills = ["Python", "Django", "Redis", "Docker", "Kubernetes"]

result = kb.enhance_match(resume_skills, job_skills)

print(f"直接匹配: {result['direct_score']}%")  # 40%
print(f"相关匹配: {result['related_score']}%")  # 基于相关技能
print(f"增强分数: {result['enhanced_score']}%") # 综合分数
```

### 场景3：技能推荐学习

```python
kb = KnowledgeBaseService()

recommendations = kb.get_skill_recommendations(
    "Python",
    target_role="后端开发",
    limit=5
)

for rec in recommendations:
    print(f"{rec['skill_name']}: {rec['suggestion']}")
```

## 🔍 关系类型说明

| 关系类型 | 说明 | 用途 |
|---------|------|------|
| co_occurrence | 共现关系 | 经常一起出现的技能 |
| similar | 相似关系 | 功能或用途相似的技能 |
| prerequisite | 前置技能 | 学习某技能前应掌握的技能 |
| same_category | 同类别 | 属于同一技术领域的技能 |
| required_for | 职业要求 | 某个职业必需掌握的技能 |

## ⚠️ 注意事项

1. **首次导入**：首次使用需要运行导入脚本，可能需要几分钟时间
2. **数据更新**：可以通过重新运行导入脚本来更新数据
3. **内存占用**：图谱数据会占用一定内存，建议有至少4GB可用内存
4. **并发访问**：SQLite支持多读但写入会锁定，建议使用单例模式

## 📝 维护指南

### 备份数据

```bash
# 备份数据库
cp modules/knowledge_base/data/knowledge_base.db backup/

# 备份图谱
cp modules/knowledge_base/data/skill_graph.gpickle backup/
```

### 清理数据

```bash
# 删除数据库文件
rm modules/knowledge_base/data/knowledge_base.db

# 删除图谱文件
rm modules/knowledge_base/data/skill_graph.gpickle

# 重新导入
python scripts/import_job_sdf.py --rebuild
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。

## 📬 联系方式

如有问题，请联系开发团队。
