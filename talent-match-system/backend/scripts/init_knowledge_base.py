#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库初始化脚本
初始化知识库数据库，加载标准技能数据
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def init_knowledge_base():
    """初始化知识库"""
    print("=" * 70)
    print("INITIALIZING KNOWLEDGE BASE")
    print("=" * 70)

    try:
        print("\n[1/3] Importing knowledge base module...")
        from modules.knowledge_base import KnowledgeBaseDB
        print("SUCCESS: Module imported")

        print("\n[2/3] Initializing database...")
        db = KnowledgeBaseDB()
        print("SUCCESS: Database initialized")

        print("\n[3/3] Verifying data...")
        skill_count = db.get_skill_count()
        print(f"SUCCESS: Total skills: {skill_count}")

        if skill_count > 0:
            print("\nSKILL CATEGORY STATISTICS:")
            skills = db.get_all_skills()
            categories = {}
            for skill in skills:
                cat = skill.get('category', 'Other')
                if cat not in categories:
                    categories[cat] = 0
                categories[cat] += 1

            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {cat}: {count} skills")

            print("\nSAMPLE SKILLS:")
            sample_skills = skills[:10]
            for skill in sample_skills:
                print(f"   - [{skill['skill_id']}] {skill['skill_name']} ({skill.get('category', 'Unknown')})")

        db.close()

        print("\n" + "=" * 70)
        print("SUCCESS: Knowledge base initialized!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\nERROR: Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_base():
    """测试知识库功能"""
    print("\n" + "=" * 70)
    print("TESTING KNOWLEDGE BASE FUNCTIONALITY")
    print("=" * 70)

    try:
        from modules.knowledge_base import KnowledgeBaseService

        print("\n[1] Testing skill query...")
        kb = KnowledgeBaseService()

        test_skills = ["Python", "java", "js", "React", "Vue.js", "Machine Learning"]
        for skill_name in test_skills:
            result = kb.normalize_skill(skill_name)
            print(f"   {skill_name} -> {result['normalized']} (confidence: {result['confidence']})")

        print("\n[2] Testing skill normalization and matching...")
        resume_skills = ["python", "Django", "PostgreSQL", "Git"]
        job_skills = ["Python", "Django", "Redis", "Docker", "Kubernetes"]

        match_result = kb.enhance_match(resume_skills, job_skills)
        print(f"   Direct match score: {match_result['direct_score']}%")
        print(f"   Related match score: {match_result['related_score']}%")
        print(f"   Enhanced score: {match_result['enhanced_score']}%")

        print("\n[3] Testing skill recommendations...")
        recommendations = kb.get_skill_recommendations("Python", limit=5)
        print(f"   Python related skills recommendations:")
        for rec in recommendations[:5]:
            print(f"   - {rec['skill_name']}: {rec['suggestion']}")

        kb.close()

        print("\n" + "=" * 70)
        print("SUCCESS: All tests passed!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("TALENT MATCHING SYSTEM - KNOWLEDGE BASE INITIALIZATION")
    print("=" * 70 + "\n")

    success = True

    if not init_knowledge_base():
        success = False

    if success:
        if not test_knowledge_base():
            success = False

    print("\n" + "=" * 70)
    if success:
        print("SUCCESS: Knowledge base initialized and tested!")
        print("Next: Integrate knowledge base into match service.")
    else:
        print("WARNING: Errors occurred during initialization or testing.")
    print("=" * 70 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
