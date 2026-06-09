
"""
数据驱动的权重学习系统
基于历史匹配、投递、收藏数据学习最优权重
"""
import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class WeightConfig:
    """权重配置"""
    skills: float = 0.4
    experience: float = 0.25
    education: float = 0.15
    certificates: float = 0.1
    location: float = 0.1

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)

    def normalize(self) -> 'WeightConfig':
        """归一化权重，确保总和为1"""
        total = sum(self.to_dict().values())
        if total > 0:
            for key in self.__dict__:
                if key in ['skills', 'experience', 'education', 'certificates', 'location']:
                    self.__dict__[key] /= total
        return self


@dataclass
class LearningSample:
    """学习样本"""
    resume_id: int
    job_id: int
    match_score: float
    dimension_scores: Dict[str, float]
    is_positive: bool  # 是否为正向样本（成功投递/录用）
    timestamp: datetime


class WeightLearner:
    """权重学习器"""

    def __init__(self, db_path: str = "talent_match.db", storage_path: str = "data/weights.json"):
        self.db_path = db_path
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.current_weights = self._load_weights()
        self.learning_rate = 0.01
        self.sample_buffer: List[LearningSample] = []
        self.industry_weights: Dict[str, WeightConfig] = {}

    def _load_weights(self) -> WeightConfig:
        """加载权重配置"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    weights = WeightConfig(**data.get('global', {}))
                    if 'industry' in data:
                        self.industry_weights = {
                            k: WeightConfig(**v) 
                            for k, v in data['industry'].items()
                        }
                    return weights
            except Exception as e:
                print(f"[WeightLearner] 加载权重失败: {e}")
        return WeightConfig()

    def _save_weights(self):
        """保存权重配置"""
        data = {
            'global': self.current_weights.to_dict(),
            'industry': {k: v.to_dict() for k, v in self.industry_weights.items()},
            'updated_at': datetime.now().isoformat()
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_weights(self, industry: Optional[str] = None) -> WeightConfig:
        """获取权重配置，支持按行业区分"""
        if industry and industry in self.industry_weights:
            return self.industry_weights[industry]
        return self.current_weights

    def collect_samples_from_db(self, days: int = 30) -> List[LearningSample]:
        """从数据库收集学习样本"""
        samples = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            # 获取投递记录作为正向样本
            cursor.execute("""
                SELECT d.resume_id, d.job_id, m.match_score, m.match_tags, 
                       m.gap_tags, d.status, d.created_at
                FROM deliveries d
                LEFT JOIN matches m ON d.resume_id = m.resume_id AND d.job_id = m.job_id
                WHERE d.created_at >= ?
            """, (cutoff_date,))

            for row in cursor.fetchall():
                sample = self._create_sample_from_row(row, is_positive=True)
                if sample:
                    samples.append(sample)

            # 获取收藏记录作为正向样本
            cursor.execute("""
                SELECT jf.user_id, jf.job_id, jf.created_at
                FROM job_favorites jf
                WHERE jf.created_at >= ?
            """, (cutoff_date,))

            for row in cursor.fetchall():
                # 简化处理，收藏视为弱正向样本
                pass

            conn.close()
        except Exception as e:
            print(f"[WeightLearner] 从数据库收集样本失败: {e}")

        return samples

    def _create_sample_from_row(self, row: sqlite3.Row, is_positive: bool) -> Optional[LearningSample]:
        """从数据库行创建学习样本"""
        try:
            # 简化版：实际需要从各维度重新计算分数
            dimension_scores = {
                'skills': 0.0,
                'experience': 0.0,
                'education': 0.0,
                'certificates': 0.0,
                'location': 0.0
            }

            # 如果有匹配记录，尝试从gap_tags推断
            if row.get('gap_tags'):
                gap_tags = json.loads(row['gap_tags'])
                # 简单逻辑：缺失越多的维度分数越低
                pass

            return LearningSample(
                resume_id=row['resume_id'],
                job_id=row['job_id'],
                match_score=row.get('match_score', 0) or 0,
                dimension_scores=dimension_scores,
                is_positive=is_positive,
                timestamp=datetime.fromisoformat(row['created_at'])
            )
        except Exception as e:
            print(f"[WeightLearner] 创建样本失败: {e}")
            return None

    def add_sample(self, sample: LearningSample):
        """添加学习样本"""
        self.sample_buffer.append(sample)
        # 保留最近1000个样本
        if len(self.sample_buffer) > 1000:
            self.sample_buffer = self.sample_buffer[-1000:]

    def learn_weights(self, iterations: int = 100) -> WeightConfig:
        """学习最优权重"""
        if not self.sample_buffer:
            print("[WeightLearner] 没有样本数据，使用默认权重")
            return self.current_weights

        # 简单的梯度下降学习
        weights = self.current_weights.to_dict()
        dimensions = list(weights.keys())

        for _ in range(iterations):
            gradients = {d: 0.0 for d in dimensions}

            for sample in self.sample_buffer:
                # 计算预测分数
                predicted = sum(
                    weights[d] * sample.dimension_scores.get(d, 0)
                    for d in dimensions
                )

                # 目标分数：正向样本希望更高，负向样本希望更低
                target = 1.0 if sample.is_positive else 0.0
                error = predicted - target

                # 计算梯度
                for d in dimensions:
                    gradients[d] += error * sample.dimension_scores.get(d, 0)

            # 更新权重
            for d in dimensions:
                weights[d] -= self.learning_rate * gradients[d]
                # 确保权重非负
                weights[d] = max(0, weights[d])

        # 更新权重并归一化
        self.current_weights = WeightConfig(**weights).normalize()
        self._save_weights()

        print(f"[WeightLearner] 学习完成: {self.current_weights}")
        return self.current_weights

    def get_industry_specific_weights(self, industry: str) -> WeightConfig:
        """获取行业特定权重，如果没有则使用行业模板"""
        if industry in self.industry_weights:
            return self.industry_weights[industry]

        # 使用行业模板
        template = self._get_industry_template(industry)
        self.industry_weights[industry] = template
        self._save_weights()
        return template

    def _get_industry_template(self, industry: str) -> WeightConfig:
        """获取行业权重模板"""
        industry_lower = industry.lower()
        
        templates = {
            'tech': WeightConfig(skills=0.5, experience=0.25, education=0.1, certificates=0.1, location=0.05),
            'finance': WeightConfig(skills=0.3, experience=0.3, education=0.2, certificates=0.15, location=0.05),
            'medical': WeightConfig(skills=0.35, experience=0.25, education=0.25, certificates=0.1, location=0.05),
            'education': WeightConfig(skills=0.3, experience=0.3, education=0.25, certificates=0.1, location=0.05),
            'design': WeightConfig(skills=0.45, experience=0.25, education=0.15, certificates=0.08, location=0.07),
        }

        # 关键词匹配
        for keyword, template in templates.items():
            if keyword in industry_lower:
                return template

        # 默认模板
        return WeightConfig()

    def analyze_weight_importance(self) -> Dict[str, float]:
        """分析各维度重要性"""
        if not self.sample_buffer:
            return self.current_weights.to_dict()

        # 简单分析：计算各维度分数方差
        dimension_scores = {d: [] for d in self.current_weights.to_dict().keys()}

        for sample in self.sample_buffer:
            for d, score in sample.dimension_scores.items():
                dimension_scores[d].append(score)

        # 方差越大的维度越重要（区分度高）
        importance = {}
        for d, scores in dimension_scores.items():
            if scores:
                importance[d] = np.var(scores)
            else:
                importance[d] = 0

        # 归一化重要性
        total = sum(importance.values())
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}

        return importance

    def manual_adjust_weights(self, adjustments: Dict[str, float]):
        """手动调整权重"""
        weights = self.current_weights.to_dict()
        for d, delta in adjustments.items():
            if d in weights:
                weights[d] = max(0, weights[d] + delta)

        self.current_weights = WeightConfig(**weights).normalize()
        self._save_weights()
        print(f"[WeightLearner] 手动调整完成: {self.current_weights}")

    def export_weight_report(self) -> Dict[str, Any]:
        """导出权重报告"""
        return {
            'current_weights': self.current_weights.to_dict(),
            'sample_count': len(self.sample_buffer),
            'industry_weights': {k: v.to_dict() for k, v in self.industry_weights.items()},
            'importance_analysis': self.analyze_weight_importance(),
            'updated_at': datetime.now().isoformat()
        }
