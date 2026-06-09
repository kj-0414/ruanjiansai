# 人才智能匹配系统 - 项目架构文档

## 1. 项目概述

本项目是一个人才智能匹配系统，基于 FastAPI 构建的后端服务，提供简历管理、岗位管理、智能匹配等核心功能。系统采用模块化架构设计，支持求职者和企业用户的双向匹配。

## 2. 目录结构

```
backend/                              # 后端应用根目录
├── api/                              # REST API路由层
│   ├── job.py                        # 岗位管理接口
│   ├── match.py                      # 智能匹配接口
│   ├── resume.py                     # 简历管理接口
│   └── user.py                       # 用户认证接口
├── config/                           # 配置文件目录
│   └── industry_templates.py         # 行业模板配置
├── database/                         # 数据库脚本
│   ├── dm_create_tables.sql          # 建表脚本
│   ├── dm_init.sql                   # 初始化脚本
│   └── dm_insert_data.sql            # 数据插入脚本
├── docs/                             # 项目文档
│   └── migration_report.md           # 迁移报告
├── graph_db/                         # 图数据库模块
│   ├── data/                         # 图数据文件
│   ├── storage/                      # 图数据存储
│   ├── __init__.py
│   └── core.py                       # 图数据库核心逻辑
├── models/                           # 数据库模型（统一管理）
│   └── __init__.py                   # SQLAlchemy模型定义
├── modules/                          # 业务模块（内部逻辑）
│   ├── admin/                        # 管理员模块
│   │   ├── __init__.py
│   │   ├── admin_controller.py       # 控制器（处理请求）
│   │   ├── admin_service.py          # 服务层（业务逻辑）
│   │   ├── admin_repository.py       # 仓储层（数据访问）
│   │   ├── schemas.py                # 数据模型（Pydantic）
│   │   └── exceptions.py             # 异常定义
│   ├── ai/                           # AI能力分析模块
│   ├── auth/                         # 用户认证模块
│   ├── common/                       # 公共模块
│   ├── job/                          # 岗位管理模块
│   ├── match/                        # 智能匹配模块
│   ├── message/                      # 消息系统模块
│   ├── resume/                       # 简历管理模块
│   └── storage/                      # 文件存储模块
├── scripts/                          # 运维脚本
│   ├── add_columns.py                # 添加列脚本
│   ├── add_user.py                   # 添加用户脚本
│   ├── check_auth.py                 # 认证检查脚本
│   └── create_admin.py               # 创建管理员脚本
├── tests/                            # 测试文件
│   └── test_api.py                   # API测试
├── uploads/                          # 文件上传目录
│   ├── job_requirements/             # 岗位需求文件
│   └── temp/                         # 临时文件
├── utils/                            # 工具函数
│   ├── ai_ability_analyzer.py        # AI能力分析器
│   ├── auth.py                       # 认证工具
│   ├── graph_generator.py            # 图谱生成器
│   ├── langchain_resume_parser.py    # LangChain简历解析器
│   ├── prompt_templates.py           # 提示词模板
│   ├── qwen_client.py                # Qwen API客户端
│   ├── resume_parser.py              # 简历解析器
│   └── semantic_matcher.py           # 语义匹配器
├── main.py                           # 应用入口
├── requirements.txt                  # 依赖列表
└── start_backend.bat                 # 启动脚本
```

## 3. 模块职责说明

### 3.1 API层 (`api/`)

负责对外暴露RESTful接口，处理HTTP请求和响应：

| 文件 | 职责 | 主要接口 |
|------|------|----------|
| `user.py` | 用户注册、登录、认证 | `/api/user/login`, `/api/user/register`, `/api/user/me` |
| `resume.py` | 简历上传、查询、更新、删除 | `/api/resume/upload`, `/api/resume/{id}` |
| `job.py` | 岗位创建、查询、更新、删除 | `/api/job`, `/api/job/{id}` |
| `match.py` | 智能匹配、推荐 | `/api/match`, `/api/match/recommendations` |

### 3.2 业务模块 (`modules/`)

采用 **Controller-Service-Repository** 三层架构模式：

| 模块 | 职责 | 核心功能 |
|------|------|----------|
| `admin` | 管理员功能 | 用户管理、系统统计 |
| `ai` | AI能力分析 | 能力树生成、雷达图分析 |
| `auth` | 用户认证 | 验证码、注册、登录、Token管理 |
| `common` | 公共组件 | 配置管理、数据库连接 |
| `job` | 岗位管理 | 岗位CRUD、需求解析 |
| `match` | 匹配算法 | 能力树匹配、相似度计算 |
| `message` | 消息系统 | 对话管理、消息推送 |
| `resume` | 简历管理 | 简历解析、结构化存储 |
| `storage` | 文件存储 | 文件上传、下载、管理 |

每个模块包含以下文件：
- `controller.py` - 控制器，处理HTTP请求
- `service.py` - 服务层，封装业务逻辑
- `repository.py` - 仓储层，数据访问抽象
- `schemas.py` - Pydantic数据模型
- `exceptions.py` - 自定义异常

### 3.3 数据模型 (`models/`)

统一管理所有SQLAlchemy数据库模型：

| 模型 | 说明 |
|------|------|
| `User` | 用户信息（手机号、密码、角色） |
| `Resume` | 简历信息（个人信息、技能、项目经历） |
| `Job` | 岗位信息（岗位描述、技能要求、公司信息） |
| `Match` | 匹配记录（匹配分数、匹配标签、能力图谱） |
| `Delivery` | 简历投递记录 |
| `JobFavorite` | 岗位收藏记录 |
| `Conversation` | 对话会话 |
| `Message` | 消息记录 |

### 3.4 工具函数 (`utils/`)

提供通用工具能力：

| 文件 | 职责 |
|------|------|
| `ai_ability_analyzer.py` | AI驱动的能力分析 |
| `auth.py` | JWT Token生成、用户认证 |
| `graph_generator.py` | 能力图谱生成 |
| `langchain_resume_parser.py` | 基于LangChain的简历解析 |
| `prompt_templates.py` | AI提示词模板管理 |
| `qwen_client.py` | Qwen大模型API客户端 |
| `resume_parser.py` | 简历文本解析（正则方式） |
| `semantic_matcher.py` | 语义相似度匹配算法 |

## 4. 核心业务流程

### 4.1 用户注册登录流程

```
用户请求 → API层(user.py) → AuthController → AuthService → JWT Token → 返回响应
```

### 4.2 简历上传与解析流程

```
上传文件 → API层(resume.py) → ResumeController → ResumeService → AI解析 → 结构化存储
```

### 4.3 岗位创建流程

```
创建请求 → API层(job.py) → JobController → JobService → 解析需求 → 提取技能 → 保存岗位信息
```

### 4.4 智能匹配流程

```
匹配请求 → API层(match.py) → MatchController → MatchService → 构建能力树 → 计算相似度 → 生成匹配结果
```

## 5. 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 框架 | FastAPI | 0.104+ |
| 数据库 | 达梦数据库 | DM8 |
| ORM | SQLAlchemy | 2.0+ |
| 认证 | JWT (PyJWT) | - |
| 密码加密 | Werkzeug | 2.3+ |
| AI服务 | 阿里云Qwen | API调用 |
| 文件处理 | python-docx, PyPDF2 | - |
| LangChain | langchain_community | 0.1+ |

## 6. 配置与部署

### 6.1 配置文件

配置文件位于 `modules/common/config.py`：

```python
# 数据库配置
DATABASE_URL: str = "dm+dmPython://SYSDBA:Dameng123@localhost:5236"

# JWT配置
SECRET_KEY: str = "your-secret-key"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# AI配置
QWEN_API_KEY: str = "your-api-key"
QWEN_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
```

### 6.2 启动方式

```bash
# 开发模式
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 7. API文档

启动服务后访问：

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## 8. 代码规范

### 8.1 命名规范

- 文件名：小写字母+下划线（`user_service.py`）
- 类名：大驼峰（`AuthService`）
- 函数名：小写字母+下划线（`get_user_info`）
- 变量名：小写字母+下划线（`user_id`）

### 8.2 架构原则

1. **单一职责**：每个模块/函数只负责一个功能
2. **依赖注入**：通过FastAPI Depends机制管理依赖
3. **三层架构**：Controller → Service → Repository
4. **异常处理**：统一的错误处理和日志记录

## 9. 安全注意事项

1. JWT Token存储在客户端，服务端无状态认证
2. 密码使用Werkzeug进行哈希加密
3. 文件上传限制大小（10MB）和类型（PDF/DOCX/图片）
4. SQLAlchemy参数化查询，防止SQL注入
5. CORS配置限制允许的来源

## 10. 目录职责总结

| 目录 | 层级 | 职责说明 |
|------|------|----------|
| `api/` | 第1层 | 对外REST API接口 |
| `modules/` | 第2层 | 业务逻辑层（Controller-Service-Repository） |
| `models/` | 第3层 | 数据库模型定义 |
| `utils/` | 工具层 | 通用工具函数 |
| `config/` | 配置层 | 应用配置 |
| `database/` | 数据层 | SQL脚本 |
| `scripts/` | 运维层 | 运维脚本 |
| `tests/` | 测试层 | 测试文件 |
| `docs/` | 文档层 | 项目文档 |
| `uploads/` | 存储层 | 上传文件 |