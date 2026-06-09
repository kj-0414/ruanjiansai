
"""
数据驱动权重系统使用示例
演示如何使用WeightLearner和增强的MatchAgent
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from modules.agents.match_agent import MatchAgent
from modules.agents.weight_learner import WeightLearner, LearningSample, WeightConfig
from datetime import datetime

def demo_weight_learner():
    """演示权重学习器的基本用法"""
    print("=" * 60)
    print("数据驱动权重系统 - 演示")
    print("=" * 60)

    # 1. 初始化权重学习器
    print("\n[1] 初始化权重学习器...")
    learner = WeightLearner(db_path="talent_match.db", storage_path="data/weights_demo.json")
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

    return learner

def demo_match_agent_with_weights():
    """演示MatchAgent与权重学习器集成"""
    print("\n" + "=" * 60)
    print("MatchAgent 与数据驱动权重集成 - 演示")
    print("=" * 60)

    # 1. 初始化MatchAgent
    print("\n[1] 初始化MatchAgent (启用数据驱动权重)...")
    match_agent = MatchAgent(use_data_driven_weights=True)
    print(f"   当前权重: {match_agent.weights}")

    # 2. 准备测试数据
    print("\n[2] 准备测试数据...")
    resume_profile = {
        "name": "张三",
        "education": "本科",
        "experience_years": "3年",
        "skills": ["Python", "Java", "MySQL", "Git"],
        "location": "北京"
    }

    job_profile = {
        "job_name": "高级Python开发工程师",
        "required_education": "本科",
        "required_experience": "3年",
        "required_skills": ["Python", "Java", "MySQL", "Docker", "FastAPI"],
        "location": "北京"
    }

    # 3. 进行匹配（默认权重）
    print("\n[3] 执行匹配（使用全局权重）...")
    result = match_agent.calculate_match(resume_profile, job_profile)
    print(f"   匹配分数: {result['match_score']}")
    print(f"   各维度分数:")
    print(f"     - 技能: {result['skill_score']} (权重: {match_agent.weights['skills']})")
    print(f"     - 经验: {result['experience_score']} (权重: {match_agent.weights['experience']})")
    print(f"     - 学历: {result['education_score']} (权重: {match_agent.weights['education']})")

    # 4. 使用行业特定权重
    print("\n[4] 执行匹配（使用技术行业权重）...")
    result_tech = match_agent.calculate_match(resume_profile, job_profile, industry="tech")
    print(f"   匹配分数: {result_tech['match_score']}")
    print(f"   使用权重: {result_tech['weights']}")

    # 5. 记录反馈
    print("\n[5] 记录用户反馈（用于权重学习）...")
    match_agent.record_match_feedback(
        resume_id=1, job_id=1, is_positive=True,
        resume_profile=resume_profile, job_profile=job_profile
    )

    # 6. 触发权重学习
    print("\n[6] 触发权重学习...")
    new_weights = match_agent.trigger_weight_learning()
    print(f"   更新后权重: {new_weights}")

    # 7. 查看权重报告
    print("\n[7] 权重报告...")
    report = match_agent.get_weight_report()
    print(f"   样本数量: {report['sample_count']}")
    print(f"   当前权重: {report['current_weights']}")

    return match_agent

def demo_manual_adjustment():
    """演示手动调整权重"""
    print("\n" + "=" * 60)
    print("手动权重调整 - 演示")
    print("=" * 60)

    match_agent = MatchAgent(use_data_driven_weights=True)
    print(f"\n[1] 初始权重: {match_agent.weights}")

    print("\n[2] 手动调整权重（增加技能权重）...")
    match_agent.adjust_weights_manually({
        'skills': 0.1,    # 技能权重 +0.1
        'experience': -0.05  # 经验权重 -0.05
    })
    print(f"   调整后权重: {match_agent.weights}")

    print("\n[3] 获取技术行业权重...")
    tech_weights = match_agent.get_industry_weights("tech")
    print(f"   技术行业权重: {tech_weights}")

if __name__ == "__main__":
    try:
        # 演示1: 权重学习器
        learner = demo_weight_learner()

        # 演示2: MatchAgent集成
        match_agent = demo_match_agent_with_weights()

        # 演示3: 手动调整
        demo_manual_adjustment()

        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
