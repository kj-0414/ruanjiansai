# 🚀 知识库快速入门指南

## 一、安装依赖

首先安装必要的依赖包：

```bash
cd backend

# 如果使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install pandas numpy pyarrow networkx fastapi uvicorn pydantic
```

## 二、导入数据集

### 方式1：使用命令行脚本

```bash
# 进入脚本目录
cd scripts

# 运行导入脚本
python import_job_sdf.py
```

### 方式2：指定数据集路径

```bash
python import_job_sdf.py --data-dir ../benchmark-main/dataset
```

### 方式3：选择数据粒度

```bash
# 全局数据
python import_job_sdf.py --granularity global

# 公司维度数据
python import_job_sdf.py --granularity company

# 职业维度数据
python import_job_sdf.py --granularity occupation
```

## 三、运行测试

```bash
# 测试知识库功能
cd scripts
python test_knowledge_base.py
```

预期输出：
```
======================================================================
🎯 人才匹配系统 - 知识库测试
======================================================================

📦 导入知识库模块...
✅ 模块导入成功

📊 初始化知识库服务...
✅ 服务初始化成功

🔍 测试技能查询...
✅ 查询到技能: Python

🔄 测试技能标准化...
✅ 标准化结果: {...}

📊 统计信息:
   - 技能总数: 2324
   - 关系总数: 10000
   ...

🎉 所有测试通过！知识库系统运行正常。
```

## 四、在代码中使用

### 1. 基础使用示例

```python
from modules.knowledge_base import KnowledgeBaseService

# 初始化服务
kb = KnowledgeBaseService()

# 查询技能
skill = kb.get_skill_info("Python")
print(skill)

# 标准化技能名称
result = kb.normalize_skill("python")
print(result)

# 关闭连接
kb.close()
```

### 2. 人岗匹配增强

```python
from modules.knowledge_base import KnowledgeBaseService

kb = KnowledgeBaseService()

# 简历技能
resume_skills = ["Python", "Django", "PostgreSQL", "Git", "Linux"]

# 岗位要求
job_skills = ["Python", "Django", "Redis", "Docker", "Kubernetes", "MySQL"]

# 增强匹配
result = kb.enhance_match(resume_skills, job_skills)

print(f"直接匹配: {result['direct_score']}%")
print(f"相关匹配: {result['related_score']}%")
print(f"增强分数: {result['enhanced_score']}%")
print(f"缺失技能: {result['missing_skills']}")
print(f"推荐技能: {result['unrecognized_skills']}")
```

### 3. 技能推荐

```python
from modules.knowledge_base import KnowledgeBaseService

kb = KnowledgeBaseService()

# 基于已有技能推荐
recommendations = kb.get_skill_recommendations(
    "Python",
    target_role="后端开发",
    limit=10
)

for rec in recommendations:
    print(f"{rec['skill_name']}: {rec['suggestion']}")
```

## 五、启动 API 服务

### 1. 在 main.py 中注册路由

在 `backend/main.py` 中添加：

```python
from modules.knowledge_base.knowledge_base_controller import router as kb_router

app.include_router(kb_router)
```

### 2. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试 API

```bash
# 查询技能
curl http://localhost:8000/api/knowledge-base/query \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"skill_name": "Python"}'

# 获取热门技能
curl http://localhost:8000/api/knowledge-base/hot-skills

# 获取统计信息
curl http://localhost:8000/api/knowledge-base/statistics

# 健康检查
curl http://localhost:8000/api/knowledge-base/health
```

## 六、查看数据

### 1. 查看数据库

```bash
# 进入 SQLite
sqlite3 modules/knowledge_base/data/knowledge_base.db

# 查看技能总数
SELECT COUNT(*) FROM skills;

# 查看某个分类的技能
SELECT * FROM skills WHERE category = '编程语言' LIMIT 10;

# 查看关系总数
SELECT COUNT(*) FROM skill_relations;

# 查看各类关系
SELECT relation_type, COUNT(*) FROM skill_relations GROUP BY relation_type;
```

### 2. 查看图谱信息

```bash
# 查看图谱统计
cat modules/knowledge_base/data/graph_info.json
```

## 七、常见问题

### Q1: 导入脚本报错"数据目录不存在"

**解决**：
```bash
# 确认数据集路径
ls ../benchmark-main/dataset

# 如果不存在，下载数据集
git clone https://github.com/xxx/Job-SDF.git
```

### Q2: 导入很慢

**正常现象**：首次导入 2324 个技能和数万条关系需要几分钟时间。

**加速方法**：
```bash
# 只导入全局数据（最快）
python import_job_sdf.py --granularity global
```

### Q3: 测试脚本报错

**检查依赖**：
```bash
pip list | grep -E "pandas|networkx|pyarrow"
```

**重新安装**：
```bash
pip install --upgrade pandas numpy pyarrow networkx
```

## 八、集成到 Agent

### 示例：增强 ResumeParseAgent

```python
from modules.agents import ResumeParseAgent, KnowledgeBaseAgent

class EnhancedResumeParseAgent(ResumeParseAgent):
    def __init__(self):
        super().__init__()
        self.kb_agent = KnowledgeBaseAgent()

    def _extract_skills_from_text(self, text: str) -> List[dict]:
        # 原有的AI提取
        ai_skills = self._extract_skills_ai(text)

        # 知识库标准化
        validated_skills = []
        for skill_name in ai_skills:
            result = self.kb_agent.normalize_skills([skill_name])[0]

            validated_skills.append({
                'name': result['normalized'],
                'confidence': result['confidence'],
                'skill_id': result.get('skill_id')
            })

        return validated_skills
```

## 九、下一步

- 📖 查看 [详细文档](docs/knowledge_base_design.md)
- 🔧 自定义数据导入流程
- 🎨 扩展知识库功能
- 📊 集成到现有 Agent 系统

---

**有问题？**
- 查看 [常见问题](#七、常见问题)
- 查看 [GitHub Issues](链接)
- 联系开发团队
