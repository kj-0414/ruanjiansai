-- ============================================================
-- 达梦数据库初始化脚本 - 人才职位智能匹配与能力图谱系统
-- 数据库密码: Dameng123456
-- 端口: 5236
-- ============================================================

-- 连接数据库
-- DIsql SYSDBA/Dameng123456@localhost:5236

-- 检查并删除已存在的用户和表空间
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLESPACE IF EXISTS TALENT_MATCH_TS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

-- 创建表空间
CREATE TABLESPACE TALENT_MATCH_TS
DATAFILE 'TALENT_MATCH_TS.dbf' SIZE 128
AUTOEXTEND ON NEXT 32
MAXSIZE 2048;
/

-- 检查并删除已存在的用户
BEGIN
    EXECUTE IMMEDIATE 'DROP USER IF EXISTS TALENT_MATCH CASCADE';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

-- 创建用户
CREATE USER TALENT_MATCH
IDENTIFIED BY "Dameng123456"
DEFAULT TABLESPACE TALENT_MATCH_TS
DEFAULT INDEX TABLESPACE TALENT_MATCH_TS;
/

-- 授予权限
GRANT RESOURCE TO TALENT_MATCH;
GRANT CREATE TABLE TO TALENT_MATCH;
GRANT CREATE VIEW TO TALENT_MATCH;
GRANT CREATE SEQUENCE TO TALENT_MATCH;
GRANT CREATE TRIGGER TO TALENT_MATCH;
GRANT CREATE PROCEDURE TO TALENT_MATCH;
/

-- 切换用户
-- CONN TALENT_MATCH/Dameng123456@localhost:5236

-- 创建表结构

-- 用户表
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    roles TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '用户ID';
COMMENT ON COLUMN users.phone IS '手机号';
COMMENT ON COLUMN users.password IS '密码';
COMMENT ON COLUMN users.roles IS '角色列表(JSON)';
COMMENT ON COLUMN users.created_at IS '创建时间';

-- 简历表
CREATE TABLE resumes (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    resume_name VARCHAR(100) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(512) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    education VARCHAR(50),
    experience TEXT,
    skills TEXT,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_resumes_user FOREIGN KEY (user_id) REFERENCES users(id)
);

COMMENT ON TABLE resumes IS '简历表';
COMMENT ON COLUMN resumes.id IS '简历ID(自增)';
COMMENT ON COLUMN resumes.resume_name IS '简历名称';
COMMENT ON COLUMN resumes.filename IS '文件名';
COMMENT ON COLUMN resumes.filepath IS '文件路径';
COMMENT ON COLUMN resumes.user_id IS '用户ID';
COMMENT ON COLUMN resumes.name IS '姓名';
COMMENT ON COLUMN resumes.phone IS '联系电话';
COMMENT ON COLUMN resumes.email IS '邮箱';
COMMENT ON COLUMN resumes.education IS '学历';
COMMENT ON COLUMN resumes.experience IS '工作经验';
COMMENT ON COLUMN resumes.skills IS '技能列表(JSON)';
COMMENT ON COLUMN resumes.created_at IS '创建时间';

-- 岗位表
CREATE TABLE jobs (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    job_desc TEXT NOT NULL,
    salary VARCHAR(50) NOT NULL,
    location VARCHAR(50),
    work_hours VARCHAR(100),
    education_requirement VARCHAR(50),
    experience_requirement VARCHAR(50),
    recruitment_count VARCHAR(50),
    department VARCHAR(100),
    job_type VARCHAR(50),
    benefits TEXT,
    user_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_jobs_user FOREIGN KEY (user_id) REFERENCES users(id)
);

COMMENT ON TABLE jobs IS '岗位表';
COMMENT ON COLUMN jobs.id IS '岗位ID(自增)';
COMMENT ON COLUMN jobs.job_name IS '岗位名称';
COMMENT ON COLUMN jobs.job_desc IS '岗位描述';
COMMENT ON COLUMN jobs.salary IS '薪资';
COMMENT ON COLUMN jobs.location IS '工作地点';
COMMENT ON COLUMN jobs.work_hours IS '工作时间';
COMMENT ON COLUMN jobs.education_requirement IS '学历要求';
COMMENT ON COLUMN jobs.experience_requirement IS '经验要求';
COMMENT ON COLUMN jobs.recruitment_count IS '招聘人数';
COMMENT ON COLUMN jobs.department IS '部门';
COMMENT ON COLUMN jobs.job_type IS '岗位类型';
COMMENT ON COLUMN jobs.benefits IS '福利待遇';
COMMENT ON COLUMN jobs.user_id IS '用户ID';
COMMENT ON COLUMN jobs.created_at IS '创建时间';

-- 匹配记录表
CREATE TABLE matches (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    resume_id BIGINT NOT NULL,
    job_id BIGINT NOT NULL,
    match_score INT NOT NULL,
    match_tags TEXT,
    gap_tags TEXT,
    ability_graph TEXT,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_matches_resume FOREIGN KEY (resume_id) REFERENCES resumes(id),
    CONSTRAINT fk_matches_job FOREIGN KEY (job_id) REFERENCES jobs(id)
);

COMMENT ON TABLE matches IS '匹配记录表';
COMMENT ON COLUMN matches.id IS '匹配记录ID(自增)';
COMMENT ON COLUMN matches.resume_id IS '简历ID';
COMMENT ON COLUMN matches.job_id IS '岗位ID';
COMMENT ON COLUMN matches.match_score IS '匹配分数';
COMMENT ON COLUMN matches.match_tags IS '匹配点';
COMMENT ON COLUMN matches.gap_tags IS '差距点';
COMMENT ON COLUMN matches.ability_graph IS '能力图谱';
COMMENT ON COLUMN matches.created_at IS '创建时间';

-- 简历投递表
CREATE TABLE deliveries (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    resume_id BIGINT NOT NULL,
    job_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_deliveries_resume FOREIGN KEY (resume_id) REFERENCES resumes(id),
    CONSTRAINT fk_deliveries_job FOREIGN KEY (job_id) REFERENCES jobs(id)
);

COMMENT ON TABLE deliveries IS '简历投递表';
COMMENT ON COLUMN deliveries.status IS '状态: pending/viewed/contacted/rejected';

-- 岗位收藏表
CREATE TABLE job_favorites (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    job_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_favorites_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_favorites_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT uk_user_job UNIQUE (user_id, job_id)
);

COMMENT ON TABLE job_favorites IS '岗位收藏表';

-- 对话会话表
CREATE TABLE conversations (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    job_seeker_id VARCHAR(64) NOT NULL,
    company_id VARCHAR(64) NOT NULL,
    job_id BIGINT NOT NULL,
    resume_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_conversations_seeker FOREIGN KEY (job_seeker_id) REFERENCES users(id),
    CONSTRAINT fk_conversations_company FOREIGN KEY (company_id) REFERENCES users(id),
    CONSTRAINT fk_conversations_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT fk_conversations_resume FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

COMMENT ON TABLE conversations IS '对话会话表';

-- 消息表
CREATE TABLE messages (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    sender_id VARCHAR(64) NOT NULL,
    receiver_id VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    is_read INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_messages_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    CONSTRAINT fk_messages_sender FOREIGN KEY (sender_id) REFERENCES users(id),
    CONSTRAINT fk_messages_receiver FOREIGN KEY (receiver_id) REFERENCES users(id)
);

COMMENT ON TABLE messages IS '消息表';

-- AI简历解析表
CREATE TABLE ai_resume_parse (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    resume_id BIGINT,
    user_id VARCHAR(64) NOT NULL,
    raw_text TEXT NOT NULL,
    parsed_result TEXT NOT NULL,
    skills TEXT,
    experience TEXT,
    education TEXT,
    name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    parse_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    is_manual_modified INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_ai_resume_parse_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_ai_resume_parse_resume FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

COMMENT ON TABLE ai_resume_parse IS 'AI简历解析表';

-- AI岗位解析表
CREATE TABLE ai_job_parse (
    id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    job_id BIGINT,
    user_id VARCHAR(64) NOT NULL,
    raw_text TEXT NOT NULL,
    parsed_result TEXT NOT NULL,
    required_skills TEXT,
    job_requirements TEXT,
    salary_range VARCHAR(50),
    job_title VARCHAR(100),
    parse_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    is_manual_modified INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_ai_job_parse_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_ai_job_parse_job FOREIGN KEY (job_id) REFERENCES jobs(id)
);

COMMENT ON TABLE ai_job_parse IS 'AI岗位解析表';

-- 创建索引
CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_jobs_user ON jobs(user_id);
CREATE INDEX idx_matches_resume ON matches(resume_id);
CREATE INDEX idx_matches_job ON matches(job_id);
CREATE INDEX idx_matches_score ON matches(match_score);
CREATE INDEX idx_deliveries_resume ON deliveries(resume_id);
CREATE INDEX idx_deliveries_job ON deliveries(job_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
CREATE INDEX idx_favorites_user ON job_favorites(user_id);
CREATE INDEX idx_favorites_job ON job_favorites(job_id);
CREATE INDEX idx_conversations_seeker ON conversations(job_seeker_id);
CREATE INDEX idx_conversations_company ON conversations(company_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_receiver ON messages(receiver_id);
CREATE INDEX idx_ai_resume_parse_user ON ai_resume_parse(user_id);
CREATE INDEX idx_ai_resume_parse_resume ON ai_resume_parse(resume_id);
CREATE INDEX idx_ai_job_parse_user ON ai_job_parse(user_id);
CREATE INDEX idx_ai_job_parse_job ON ai_job_parse(job_id);

-- 提交
COMMIT;
