
"""
简单的权重学习系统测试
不依赖其他模块
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from modules.agents.weight_learner import WeightLearner, LearningSample, WeightConfig
from datetime import datetime

print("=" * 60)
print("数据驱动权重系统 - 简单测试")
print("=" * 60)

try:
    # 1. 初始化权重学习器
    print("\n[1] 初始化权重学习器...")
    learner = WeightLearner(db_path="talent_match.db", storage_path="data/weights_test.json")
    print(f"   初始权重: {learner.current_weights}")

    # 2. 创建一些模拟学习样本
    print("\n[2] 创建模拟学习样本...")
    samples = [
        LearningSample(
            resume_id=1, job_id=1, match_score=0.75,
            dimension_scores={'skills': 0.8, 'experience': 0.7, 'education': 0.9, 'certificates': 0.6, 'location': 1.0},
            is_positive=True, timestamp=datetime.now()
        ),
        LearningSample(
            resume_id=2, job_id=1, match_score=0.5,
            dimension_scores={'skills': 0.5, 'experience': 0.6, 'education': 0.8, 'certificates': 0.4, 'location': 0.7},
            is_positive=False, timestamp=datetime.now()
        ),
        LearningSample(
            resume_id=3, job_id=2, match_score=0.9,
            dimension_scores={'skills': 0.95, 'experience': 0.85, 'education': 0.9, 'certificates': 0.9, 'location': 0.9},
            is_positive=True, timestamp=datetime.now()
        ),
    ]

    for sample in samples:
        learner.add_sample(sample)
    print(f"   已添加 {len(samples)} 个学习样本")

    # 3. 学习权重
    print("\n[3] 开始权重学习...")
    new_weights = learner.learn_weights(iterations=50)
    print(f"   学习后权重: {new_weights}")

    # 4. 获取行业特定权重
    print("\n[4] 获取行业特定权重...")
    tech_weights = learner.get_industry_specific_weights("tech")
    finance_weights = learner.get_industry_specific_weights("finance")
    print(f"   技术行业权重: {tech_weights}")
    print(f"   金融行业权重: {finance_weights}")

    # 5. 导出权重报告
    print("\n[5] 导出权重报告...")
    report = learner.export_weight_report()
    print(f"   样本数量: {report['sample_count']}")
    print(f"   重要性分析: {report['importance_analysis']}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()

