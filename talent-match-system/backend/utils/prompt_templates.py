# 简历解析Prompt模板
RESUME_PARSE_PROMPT = """你是一个专业的简历解析助手。请从以下简历文本中提取关键信息，并以JSON格式返回。

简历文本：
{resume_text}

请提取以下信息并返回JSON格式：
{{
    "name": "姓名",
    "phone": "电话号码",
    "email": "电子邮箱",
    "education": "最高学历（如：本科、硕士、博士）",
    "experience_years": "正式工作年限（不含实习，如：3年、5年）",
    "skills": ["技能1", "技能2", "技能3"],
    "work_experience": [
        {{
            "company": "公司名称",
            "position": "职位名称",
            "duration": "工作时间",
            "description": "工作描述",
            "technologies": ["技术栈1", "技术栈2"],
            "domain": "所属领域（如：互联网、金融、医疗）"
        }}
    ],
    "internship_experience": [
        {{
            "company": "公司名称",
            "position": "实习职位名称",
            "duration": "实习时间",
            "description": "实习内容描述",
            "technologies": ["技术栈1", "技术栈2"],
            "domain": "所属领域（如：互联网、金融、医疗）"
        }}
    ],
    "education_history": [
        {{
            "school": "学校名称",
            "degree": "学历",
            "major": "专业",
            "duration": "学习时间"
        }}
    ],
    "self_evaluation": "自我评价",
    "highlights": ["亮点1", "亮点2"]
}}

注意：
1. 只返回JSON格式，不要包含其他文字
2. 如果某项信息不存在或不明确，返回"未提供"或空数组[]
3. 技能请提取具体的技术栈名称，如Python、Java、Vue等
4. 工作经历和实习经历要严格区分：正式工作是毕业后的全职工作，实习是在校期间的实践经历
5. 从工作经历和实习经历中都要提取技术栈和所属领域
6. 工作经历、实习经历和学历按时间倒序排列（最新的在前）
7. 如果没有实习经历，internship_experience返回空数组[]
"""

# 职位说明书解析Prompt模板
JOB_PARSE_PROMPT = """你是一个专业的职位说明书解析助手。请从以下职位说明书文本中提取关键信息，并以JSON格式返回。

职位说明书文本：
{job_text}

请提取以下信息并返回JSON格式：
{{
    "job_title": "岗位名称",
    "salary_range": "薪资范围（如：15K-25K、面议）",
    "location": "工作地点",
    "job_type": "工作类型（如：全职、兼职、实习）",
    "required_skills": ["技能1", "技能2", "技能3"],
    "required_education": "学历要求（如：本科及以上、硕士优先）",
    "required_experience": "经验要求（如：3年以上、应届毕业生）",
    "job_responsibilities": ["职责1", "职责2", "职责3"],
    "job_requirements": ["要求1", "要求2", "要求3"],
    "benefits": ["福利1", "福利2", "福利3"],
    "company_intro": "公司简介（如果提供）",
    "highlights": ["岗位亮点1", "岗位亮点2"]
}}

注意：
1. 只返回JSON格式，不要包含其他文字
2. 如果某项信息不存在或不明确，返回"未提供"
3. 技能请提取具体的技术栈名称，如Python、Java、Vue等
4. 职责和要求请用简洁的语言描述
"""

# 匹配分析Prompt模板
MATCH_ANALYSIS_PROMPT = """你是一个专业的人才匹配分析师。请分析以下简历和职位说明书的匹配度，并给出详细建议。

简历信息：
{resume_info}

职位信息：
{job_info}

请分析并返回JSON格式：
{{
    "match_score": 匹配分数（0-100）,
    "match_strengths": ["匹配优势1", "匹配优势2"],
    "match_gaps": ["匹配差距1", "匹配差距2"],
    "suggestions": ["改进建议1", "改进建议2"],
    "interview_tips": ["面试建议1", "面试建议2"],
    "career_advice": "职业发展建议"
}}

注意：
1. 只返回JSON格式，不要包含其他文字
2. match_score根据简历与职位的匹配程度计算，0-100分
3. match_strengths列出简历中符合职位要求的优势
4. match_gaps列出简历中缺少的技能或经验
5. suggestions给出具体的改进建议
"""

# 五维分析Prompt模板
FIVE_DIMENSION_ANALYSIS_PROMPT = """你是一个专业的人才能力分析师。请根据以下简历信息，进行五维分析，包括专业技能、项目经历、学历背景、证书资质、软技能。

简历信息：
{resume_info}

请进行五维分析并返回JSON格式：
{{
    "analysis": {{
        "professional_skills": {{
            "score": 专业技能评分（0-100）,
            "description": "专业技能分析描述",
            "strengths": ["优势1", "优势2"],
            "weaknesses": ["不足1", "不足2"]
        }},
        "project_experience": {{
            "score": 项目经历评分（0-100）,
            "description": "项目经历分析描述",
            "strengths": ["优势1", "优势2"],
            "weaknesses": ["不足1", "不足2"]
        }},
        "education_background": {{
            "score": 学历背景评分（0-100）,
            "description": "学历背景分析描述",
            "strengths": ["优势1", "优势2"],
            "weaknesses": ["不足1", "不足2"]
        }},
        "certifications": {{
            "score": 证书资质评分（0-100）,
            "description": "证书资质分析描述",
            "strengths": ["优势1", "优势2"],
            "weaknesses": ["不足1", "不足2"]
        }},
        "soft_skills": {{
            "score": 软技能评分（0-100）,
            "description": "软技能分析描述",
            "strengths": ["优势1", "优势2"],
            "weaknesses": ["不足1", "不足2"]
        }}
    }},
    "overall_evaluation": "整体评价和建议",
    "ability_map": [
        {{
            "dimension": "专业技能",
            "score": 评分（0-100）,
            "items": ["技能1", "技能2"]
        }},
        {{
            "dimension": "项目经历",
            "score": 评分（0-100）,
            "items": ["项目1", "项目2"]
        }},
        {{
            "dimension": "学历背景",
            "score": 评分（0-100）,
            "items": ["学历1", "学历2"]
        }},
        {{
            "dimension": "证书资质",
            "score": 评分（0-100）,
            "items": ["证书1", "证书2"]
        }},
        {{
            "dimension": "软技能",
            "score": 评分（0-100）,
            "items": ["软技能1", "软技能2"]
        }}
    ]
}}

注意：
1. 只返回JSON格式，不要包含其他文字
2. 每个维度的评分要根据简历中的实际情况客观评估
3. 分析描述要详细且有针对性
4. 能力图谱要清晰展示各个维度的核心内容
"""

def get_resume_prompt(resume_text: str) -> str:
    """生成简历解析Prompt"""
    return RESUME_PARSE_PROMPT.format(resume_text=resume_text)

def get_job_prompt(job_text: str) -> str:
    """生成职位说明书解析Prompt"""
    return JOB_PARSE_PROMPT.format(job_text=job_text)

def get_match_prompt(resume_info: str, job_info: str) -> str:
    """生成匹配分析Prompt"""
    return MATCH_ANALYSIS_PROMPT.format(resume_info=resume_info, job_info=job_info)

def get_five_dimension_prompt(resume_info: str) -> str:
    """生成五维分析Prompt"""
    return FIVE_DIMENSION_ANALYSIS_PROMPT.format(resume_info=resume_info)