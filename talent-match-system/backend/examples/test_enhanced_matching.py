"""
测试增强后的人岗匹配系统
验证需求权重是否生效
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.agents.match_agent import MatchAgent
from modules.knowledge_base.db import KnowledgeBaseDB

print("=" * 70)
print("Test Enhanced Matching System")
print("=" * 70)

# 1. 检查知识库增强
print("\n[1/4] Checking enhanced knowledge base...")
kb = KnowledgeBaseDB()
skills = kb.get_all_skills()

print(f"  Total skills in database: {len(skills)}")

# 统计增强字段
enhanced_count = 0
hot_count = 0
total_demand = 0
for skill in skills:
    if skill.get('demand_weight', 0) > 0:
        enhanced_count += 1
    if skill.get('is_hot_skill', 0) == 1:
        hot_count += 1
    total_demand += skill.get('avg_demand', 0)

print(f"  Skills with demand data: {enhanced_count}")
print(f"  Hot skills marked: {hot_count}")
print(f"  Total average demand: {total_demand:.2f}")

# 2. 查看热门技能
print("\n[2/4] Top 10 hot skills...")
hot_skills = [s for s in skills if s.get('demand_weight', 0) > 0]
hot_skills.sort(key=lambda x: x.get('demand_weight', 0), reverse=True)

for i, skill in enumerate(hot_skills[:10], 1):
    print(f"  {i}. {skill['skill_name']}: demand_weight={skill['demand_weight']:.4f}, "
          f"avg_demand={skill['avg_demand']:.1f}")

# 3. 测试匹配（对比是否使用需求权重）
print("\n[3/4] Testing matching with demand weights...")

match_agent = MatchAgent(use_data_driven_weights=True)

# 简历1：具备热门技能
resume1 = {
    "name": "张三",
    "skills": ["Python", "Java", "MySQL"],
    "experience_years": "3",
    "education": "本科"
}

# 简历2：具备冷门技能
resume2 = {
    "name": "李四",
    "skills": ["Cobol", "Fortran", "Pascal"],
    "experience_years": "3",
    "education": "本科"
}

# 同一岗位
job = {
    "job_name": "软件开发工程师",
    "required_skills": ["Python", "Java", "MySQL", "Cobol"],
    "required_experience": "2年",
    "required_education": "本科"
}

print("\n  Resume 1 (has hot skills: Python, Java, MySQL):")
result1 = match_agent.calculate_match(resume1, job)
print(f"    Match score: {result1['match_score']}")
print(f"    Skill score: {result1['skill_score']}")
print(f"    Matched: {result1['matched_skills']}")

print("\n  Resume 2 (has obscure skills: Cobol, Fortran, Pascal):")
result2 = match_agent.calculate_match(resume2, job)
print(f"    Match score: {result2['match_score']}")
print(f"    Skill score: {result2['skill_score']}")
print(f"    Matched: {result2['matched_skills']}")

print(f"\n  Difference: {result1['skill_score'] - result2['skill_score']:.2f} points")
if result1['skill_score'] > result2['skill_score']:
    print("  ✓ Demand-weighted matching works! Hot skills give higher scores.")
else:
    print("  ✗ No difference detected (may need adjustment)")

# 4. 建议学习技能（测试趋势分析）
print("\n[4/4] Testing learning recommendations...")
# 找一些缺失但有上升趋势的技能
missing_skills = result1.get('missing_skills', [])
if missing_skills:
    print("  Missing skills analysis:")
    for skill_name in missing_skills[:3]:
        info = kb.get_skill_info(skill_name)
        if info:
            trend = info.get('demand_trend', 0)
            avg_demand = info.get('avg_demand', 0)
            trend_str = "up" if trend > 0 else "down" if trend < 0 else "stable"
            print(f"    - {skill_name}: demand={avg_demand:.1f}, trend={trend_str}")

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
