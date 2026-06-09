"""
简单测试知识库增强
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from modules.knowledge_base.db import KnowledgeBaseDB

print("=" * 70)
print("Test Enhanced Knowledge Base")
print("=" * 70)

# 1. 检查知识库增强
print("\n[1/2] Checking enhanced knowledge base...")
kb = KnowledgeBaseDB()
skills = kb.get_all_skills()

print(f"  Total skills: {len(skills)}")

# 统计增强字段
enhanced_count = 0
hot_count = 0
for skill in skills:
    if skill.get('demand_weight', 0) > 0:
        enhanced_count += 1
    if skill.get('is_hot_skill', 0) == 1:
        hot_count += 1

print(f"  Skills with demand data: {enhanced_count}")
print(f"  Hot skills: {hot_count}")

# 2. 查看热门技能
print("\n[2/2] Top 10 hot skills by demand:")
hot_skills = [s for s in skills if s.get('demand_weight', 0) > 0]
hot_skills.sort(key=lambda x: x.get('demand_weight', 0), reverse=True)

for i, skill in enumerate(hot_skills[:10], 1):
    print(f"  {i}. {skill['skill_name']}")
    print(f"     - demand_weight: {skill.get('demand_weight', 0):.6f}")
    print(f"     - avg_demand: {skill.get('avg_demand', 0):.1f}")
    print(f"     - total_demand: {skill.get('total_demand', 0):.1f}")
    print(f"     - demand_trend: {skill.get('demand_trend', 0):.2f}")
    print(f"     - cooccurrence_count: {skill.get('cooccurrence_count', 0)}")

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
