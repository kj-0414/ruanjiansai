-- TALENT_MATCH 用户下创建表结构并导入数据

-- 用户表
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    roles TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

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

COMMIT;
EXIT;
