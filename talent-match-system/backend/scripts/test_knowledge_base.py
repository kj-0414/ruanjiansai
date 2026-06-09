#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库功能测试脚本
测试知识库的各个功能模块
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_knowledge_base():
    """测试知识库功能"""
    print("=" * 70)
    print("TEST: Starting knowledge base functionality test")
    print("=" * 70)

    try:
        print("\n[1] Importing knowledge base module...")
        from modules.knowledge_base import KnowledgeBaseService, KnowledgeBaseDB, SkillKnowledgeGraph
        print("SUCCESS: Module imported")

        print("\n[2] Initializing knowledge base service...")
        kb = KnowledgeBaseService()
        print("SUCCESS: Service initialized")

        print("\n[3] Testing skill query...")
        skill_info = kb.get_skill_info("Python")
        if skill_info:
            print(f"SUCCESS: Found skill: {skill_info.get('skill_name')}")
        else:
            print("INFO: 'Python' not found (may need to import data first)")

        print("\n[4] Testing skill normalization...")
        result = kb.normalize_skill("python")
        print(f"SUCCESS: Normalization result: {result}")

        print("\n[5] Testing related skills query...")
        if skill_info and skill_info.get('skill_id'):
            related = kb.get_related_skills(skill_info['skill_id'], max_count=5)
            print(f"SUCCESS: Found {len(related)} related skills")
        else:
            print("INFO: Skipping related skills query (no skill_id)")

        print("\n[6] Testing statistics...")
        stats = kb.get_skill_statistics()
        print(f"SUCCESS: Statistics:")
        print(f"   - Total skills: {stats.get('db_skill_count', 0)}")
        print(f"   - Total relations: {stats.get('db_relation_count', 0)}")
        print(f"   - Graph nodes: {stats.get('skill_nodes', 0)}")
        print(f"   - Graph edges: {stats.get('total_edges', 0)}")

        print("\n[7] Testing data normalizer...")
        from modules.knowledge_base.parsers import DataNormalizer
        normalizer = DataNormalizer()

        test_cases = ["javascript", "JS", "java script", "ReactJS"]
        for test in test_cases:
            normalized = normalizer.normalize_skill_name(test)
            category = normalizer.detect_category(normalized)
            print(f"   {test} -> {normalized} ({category})")

        print("\nALL TESTS PASSED!")

        kb.close()
        return True

    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_creation():
    """测试图谱创建"""
    print("\n" + "=" * 70)
    print("TEST: Testing graph creation")
    print("=" * 70)

    try:
        from modules.knowledge_base import SkillKnowledgeGraph

        print("\n[1] Creating test graph...")
        graph = SkillKnowledgeGraph()

        skills = [
            (1, "Python", "Programming Language"),
            (2, "Django", "Backend Framework"),
            (3, "Flask", "Backend Framework"),
            (4, "PostgreSQL", "Database"),
            (5, "Docker", "Container Technology")
        ]

        for skill_id, name, category in skills:
            graph.add_skill_node(skill_id, {
                'skill_name': name,
                'category': category
            })

        graph.add_skill_relation(1, 2, 'prerequisite', 0.9)
        graph.add_skill_relation(1, 3, 'prerequisite', 0.9)
        graph.add_skill_relation(1, 4, 'co_occurrence', 0.7)
        graph.add_skill_relation(2, 4, 'co_occurrence', 0.8)
        graph.add_skill_relation(2, 5, 'co_occurrence', 0.6)

        print(f"SUCCESS: Graph created:")
        print(f"   - Nodes: {graph.graph.number_of_nodes()}")
        print(f"   - Edges: {graph.graph.number_of_edges()}")

        print("\n[2] Testing related skills query...")
        related = graph.get_related_skills(1, max_depth=2)
        print(f"SUCCESS: Found {len(related)} related skills for Python")
        for r in related[:3]:
            print(f"   - {r.get('skill_name')} (relation: {r.get('relation_type')})")

        print("\n[3] Testing learning path query...")
        path = graph.get_skill_learning_path(1, 4)
        if path:
            print(f"SUCCESS: Learning path: {' -> '.join([p.get('name', '') for p in path])}")

        print("\n[4] Getting graph statistics...")
        stats = graph.get_skill_graph_stats()
        print(f"SUCCESS: Graph statistics:")
        print(f"   - Density: {stats['density']:.4f}")
        print(f"   - Average degree: {stats['avg_degree']:.2f}")

        print("\nGRAPH TEST PASSED!")
        return True

    except Exception as e:
        print(f"\nERROR: Graph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("TALENT MATCHING SYSTEM - KNOWLEDGE BASE TEST")
    print("=" * 70 + "\n")

    success = True

    if not test_knowledge_base():
        success = False

    if not test_graph_creation():
        success = False

    print("\n" + "=" * 70)
    if success:
        print("ALL TESTS PASSED! Knowledge base system is running normally.")
    else:
        print("Some tests failed. Please check error messages.")
    print("=" * 70 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
