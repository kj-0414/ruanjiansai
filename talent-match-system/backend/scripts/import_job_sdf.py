
"""
从 Job-SDF 数据集导入数据到我们的人才匹配系统
"""
import sys
from pathlib import Path
import pandas as pd
import json
import sqlite3
import shutil

# 路径设置
PROJECT_ROOT = Path(__file__).parent.parent
BENCHMARK_ROOT = Path(__file__).parent.parent.parent / 'benchmark-main'
EXTRACTED_WEIGHTS_DIR = BENCHMARK_ROOT / 'extracted_weights'
DATA_DIR = PROJECT_ROOT / 'data'

print("=" * 80)
print("Job-SDF 数据集成到人才匹配系统")
print("=" * 80)

# 1. 创建数据目录
print("\n[1/5] 创建数据目录...")
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / 'job_sdf').mkdir(exist_ok=True)

# 2. 复制提取的权重文件
print("\n[2/5] 复制权重文件...")
if EXTRACTED_WEIGHTS_DIR.exists():
    for file in EXTRACTED_WEIGHTS_DIR.glob('*'):
        shutil.copy2(file, DATA_DIR / 'job_sdf' / file.name)
        print(f"  复制: {file.name}")
else:
    print("  警告: 权重文件不存在，请先运行 benchmark-main/extract_weights.py")

# 3. 复制原始数据文件
print("\n[3/5] 复制 Job-SDF 原始数据...")
SOURCE_DATA_DIR = BENCHMARK_ROOT / 'dataset'
TARGET_DATA_DIR = DATA_DIR / 'job_sdf' / 'raw'
TARGET_DATA_DIR.mkdir(exist_ok=True)

# 只复制关键的数据文件
for cat in ['demand', 'graph', 'proportion']:
    source_dir = SOURCE_DATA_DIR / cat
    if source_dir.exists():
        for file in source_dir.glob('*.parquet'):
            if 'r0.' in file.name or 'company.' in file.name:
                shutil.copy2(file, TARGET_DATA_DIR / file.name)
                print(f"  复制: {cat}/{file.name}")

# 4. 从原始数据提取技能共现图
print("\n[4/5] 提取技能共现关系...")
try:
    graph_r0 = pd.read_parquet(TARGET_DATA_DIR / 'r0.parquet')
    print(f"  技能共现关系: {len(graph_r0)} 条")
    
    # 转换为知识图谱格式
    kg_relations = []
    for idx, row in graph_r0.iterrows():
        kg_relations.append({
            'skill_id_1': int(row['row_id']),
            'skill_id_2': int(row['col_id']),
            'relation_type': 'co_occur',
            'source': 'Job-SDF'
        })
    
    # 保存
    with open(DATA_DIR / 'job_sdf' / 'skill_cooccurrence.json', 'w', encoding='utf-8') as f:
        json.dump(kg_relations, f, ensure_ascii=False, indent=2)
    print(f"  技能共现关系已保存: skill_cooccurrence.json ({len(kg_relations)} 条)")
except Exception as e:
    print(f"  警告: 提取技能共现关系失败: {e}")

# 5. 创建集成配置文件
print("\n[5/5] 创建配置文件...")
integration_config = {
    'dataset_name': 'Job-SDF',
    'source': 'https://github.com/Job-SDF/benchmark',
    'description': '岗位技能需求预测数据集',
    'time_span': '2021-01 至 2023-12',
    'total_skills': 2335,
    'granularities': {
        'r0': 'L1-Occupation',
        'r1': 'L2-Occupation',
        'company': 'Company',
        'region': 'Region'
    },
    'recommended_weights': {
        'skills': 0.55,
        'experience': 0.20,
        'education': 0.15,
        'certificates': 0.05,
        'location': 0.05
    }
}

with open(DATA_DIR / 'job_sdf' / 'integration_config.json', 'w', encoding='utf-8') as f:
    json.dump(integration_config, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("集成完成！")
print("=" * 80)
print(f"\n📂 数据已保存到: {DATA_DIR / 'job_sdf'}")
print("\n📋 下一步:")
print("  1. 查看 data/job_sdf/integration_config.json")
print("  2. 集成到 MatchAgent，使用数据驱动的权重")
print("  3. 使用技能共现图增强知识图谱")

