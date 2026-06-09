# 生成能力图谱
def generate_ability_graph(resume_skills, job_skills):
    """
    生成能力图谱数据
    :param resume_skills: 简历中的技能集合
    :param job_skills: 岗位要求的技能集合
    :return: 能力图谱数据（ECharts格式）
    """
    # 计算技能匹配度
    resume_skill_set = set(resume_skills)
    job_skill_set = set(job_skills)
    
    # 计算匹配的技能
    match_skills = resume_skill_set.intersection(job_skill_set)
    # 计算缺失的技能
    gap_skills = job_skill_set - resume_skill_set
    
    # 计算匹配度分数
    if len(job_skill_set) > 0:
        match_score = int(len(match_skills) / len(job_skill_set) * 100)
    else:
        match_score = 0
    
    # 生成能力图谱数据
    ability_graph = {
        "indicator": [
            {"name": "技能匹配度", "max": 100},
            {"name": "学历匹配度", "max": 100},
            {"name": "经验匹配度", "max": 100},
            {"name": "专业匹配度", "max": 100},
            {"name": "综合匹配度", "max": 100}
        ],
        "data": [
            {
                "value": [
                    match_score,
                    80,  # 模拟数据
                    75,  # 模拟数据
                    85,  # 模拟数据
                    match_score
                ],
                "name": "简历与岗位匹配度"
            }
        ]
    }
    
    return ability_graph