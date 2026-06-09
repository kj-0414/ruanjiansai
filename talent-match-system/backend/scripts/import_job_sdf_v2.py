
"""
从 Job-SDF 数据集导入数据到我们的人才匹配系统 (v2)
"""
import sys
from pathlib import Path
import pandas as pd
import json
import sqlite3
import shutil

# 路径设置
PROJECT_ROOT = Path(__file__).parent.parent
BENCHMARK_ROOT = PROJECT_ROOT.parent / 'benchmark-main'
EXTRACTED_WEIGHTS_DIR = BENCHMARK_ROOT / 'extracted_weights'
DATA_DIR = PROJECT_ROOT / 'data'

print("=" * 80)
print("Job-SDF Data Integration to Talent Matching System")
print("=" * 80)

# 1. 创建数据目录
print("\n[1/5] Creating data directories...")
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / 'job_sdf').mkdir(exist_ok=True)

# 2. 复制提取的权重文件
print("\n[2/5] Copying weight files...")
if EXTRACTED_WEIGHTS_DIR.exists():
    for file in EXTRACTED_WEIGHTS_DIR.glob('*'):
        shutil.copy2(file, DATA_DIR / 'job_sdf' / file.name)
        print(f"  Copied: {file.name}")
else:
    print("  Warning: Weight files not found, please run benchmark-main/extract_weights_simple.py first")

# 3. 复制原始数据文件
print("\n[3/5] Copying Job-SDF raw data...")
SOURCE_DATA_DIR = BENCHMARK_ROOT / 'dataset'
TARGET_DATA_DIR = DATA_DIR / 'job_sdf' / 'raw'
TARGET_DATA_DIR.mkdir(exist_ok=True)

# 只复制关键的数据文件
copied_files = []
for cat in ['demand', 'graph', 'proportion']:
    source_dir = SOURCE_DATA_DIR / cat
    if source_dir.exists():
        for file in source_dir.glob('*.parquet'):
            if 'r0.' in file.name or 'company.' in file.name:
                shutil.copy2(file, TARGET_DATA_DIR / file.name)
                copied_files.append(f"{cat}/{file.name}")
                print(f"  Copied: {cat}/{file.name}")

# 4. 从原始数据提取技能共现图
print("\n[4/5] Extracting skill co-occurrence relations...")
graph_file = TARGET_DATA_DIR / 'r0.parquet'
if (BENCHMARK_ROOT / 'dataset' / 'graph' / 'r0.parquet').exists():
    # 直接从原始位置读取
    graph_r0 = pd.read_parquet(BENCHMARK_ROOT / 'dataset' / 'graph' / 'r0.parquet')
    print(f"  Skill co-occurrence relations: {len(graph_r0)}")
    
    kg_relations = []
    for idx, row in graph_r0.iterrows():
        kg_relations.append({
            'skill_id_1': int(row['row_id']),
            'skill_id_2': int(row['col_id']),
            'relation_type': 'co_occur',
            'source': 'Job-SDF'
        })
    
    with open(DATA_DIR / 'job_sdf' / 'skill_cooccurrence.json', 'w', encoding='utf-8') as f:
        json.dump(kg_relations, f, ensure_ascii=False, indent=2)
    print(f"  Skill co-occurrence relations saved: skill_cooccurrence.json ({len(kg_relations)} relations)")
else:
    print("  Warning: Graph file not found")

# 5. 创建集成配置文件
print("\n[5/5] Creating configuration file...")
integration_config = {
    'dataset_name': 'Job-SDF',
    'source': 'https://github.com/Job-SDF/benchmark',
    'description': 'Job Skill Demand Forecasting dataset',
    'time_span': '2021-01 to 2023-12',
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
print("Integration complete!")
print("=" * 80)
print(f"\nData saved to: {DATA_DIR / 'job_sdf'}")
print("\nNext steps:")
print("  1. Check data/job_sdf/integration_config.json")
print("  2. Integrate into MatchAgent with data-driven weights")
print("  3. Enhance knowledge graph with skill co-occurrence data")

