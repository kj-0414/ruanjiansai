"""
从 Job-SDF 数据集提取数据，增强知识库
"""
import sys
from pathlib import Path
import pandas as pd
import json
import numpy as np
import sqlite3

PROJECT_ROOT = Path(__file__).parent.parent
BENCHMARK_ROOT = PROJECT_ROOT.parent.parent / 'benchmark-main'
DB_PATH = PROJECT_ROOT / 'modules' / 'knowledge_base' / 'data' / 'knowledge_base.db'

print("=" * 70)
print("Enhance Knowledge Base with Job-SDF Data")
print("=" * 70)

# 1. 读取 Job-SDF 数据
print("\n[1/5] Reading Job-SDF data...")
demand_r0 = pd.read_parquet(BENCHMARK_ROOT / 'dataset' / 'demand' / 'r0.parquet')
graph_r0 = pd.read_parquet(BENCHMARK_ROOT / 'dataset' / 'graph' / 'r0.parquet')
print(f"  Demand data: {demand_r0.shape}")
print(f"  Graph data: {graph_r0.shape}")

# 2. 提取时间列
time_cols = [col for col in demand_r0.columns if col.startswith('20')]
print(f"\n  Time span: {len(time_cols)} months")

# 3. 计算每个技能的需求统计
print("\n[2/5] Calculating skill demand statistics...")
skill_stats = {}
for idx, row in demand_r0.iterrows():
    skill_id = int(row['skill_id'])
    demands = row[time_cols].values
    
    skill_stats[skill_id] = {
        'total_demand': float(np.sum(demands)),
        'avg_demand': float(np.mean(demands)),
        'max_demand': float(np.max(demands)),
        'demand_trend': float(np.polyfit(range(len(demands)), demands, 1)[0])
    }

print(f"  Calculated stats for {len(skill_stats)} skills")

# 4. 计算技能共现次数
print("\n[3/5] Calculating co-occurrence counts...")
cooccurrence_counts = {}
for idx, row in graph_r0.iterrows():
    skill1 = int(row['row_id'])
    skill2 = int(row['col_id'])
    
    cooccurrence_counts[skill1] = cooccurrence_counts.get(skill1, 0) + 1
    cooccurrence_counts[skill2] = cooccurrence_counts.get(skill2, 0) + 1

print(f"  Calculated co-occurrence for {len(cooccurrence_counts)} skills")

# 5. 计算需求权重
print("\n[4/5] Calculating demand weights...")
total_avg_demand = sum(s['avg_demand'] for s in skill_stats.values())
for skill_id, stats in skill_stats.items():
    stats['demand_weight'] = stats['avg_demand'] / total_avg_demand if total_avg_demand > 0 else 0

# 6. 更新数据库
print("\n[5/5] Updating knowledge base...")
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# 先更新表结构（添加新列）
print("  Updating table structure...")
try:
    cursor.execute("ALTER TABLE skills ADD COLUMN demand_weight REAL DEFAULT 0.0")
    cursor.execute("ALTER TABLE skills ADD COLUMN avg_demand REAL DEFAULT 0.0")
    cursor.execute("ALTER TABLE skills ADD COLUMN total_demand REAL DEFAULT 0.0")
    cursor.execute("ALTER TABLE skills ADD COLUMN demand_trend REAL DEFAULT 0.0")
    cursor.execute("ALTER TABLE skills ADD COLUMN cooccurrence_count INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE skills ADD COLUMN source TEXT DEFAULT 'manual'")
    conn.commit()
    print("  Table structure updated")
except Exception as e:
    print(f"  Table structure already exists or error: {e}")

# 获取现有技能数量
cursor.execute("SELECT COUNT(*) FROM skills")
existing_count = cursor.fetchone()[0]
print(f"  Existing skills in database: {existing_count}")

# 更新每个技能的统计数据
updated_count = 0
for skill_id, stats in skill_stats.items():
    cooccurrence = cooccurrence_counts.get(skill_id, 0)
    
    cursor.execute("""
        UPDATE skills 
        SET demand_weight = ?,
            avg_demand = ?,
            total_demand = ?,
            demand_trend = ?,
            cooccurrence_count = ?,
            source = 'job_sdf',
            updated_at = CURRENT_TIMESTAMP
        WHERE skill_id = ?
    """, (
        stats['demand_weight'],
        stats['avg_demand'],
        stats['total_demand'],
        stats['demand_trend'],
        cooccurrence,
        skill_id
    ))
    
    if cursor.rowcount > 0:
        updated_count += 1

conn.commit()
print(f"  Updated {updated_count} skills")

# 标记热门技能（需求权重 > 0.001）
cursor.execute("""
    UPDATE skills 
    SET is_hot_skill = 1 
    WHERE demand_weight > 0.001
""")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM skills WHERE is_hot_skill = 1")
hot_count = cursor.fetchone()[0]
print(f"  Hot skills marked: {hot_count}")

conn.close()

print("\n" + "=" * 70)
print("Enhancement Complete!")
print("=" * 70)
print(f"\nUpdated skills: {updated_count}")
print(f"Hot skills: {hot_count}")
print(f"\nNew fields added:")
print("  - demand_weight: Skill demand weight (relative importance)")
print("  - avg_demand: Average monthly demand")
print("  - total_demand: Total demand over 36 months")
print("  - demand_trend: Demand trend (positive = growing)")
print("  - cooccurrence_count: Number of co-occurrences")
print("  - source: Data source (job_sdf)")

