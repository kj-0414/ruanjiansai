"""
时序数据加载器
将技能需求时序数据加载到知识库
"""

import logging
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path

from ..db import KnowledgeBaseDB
from ..parsers import ParquetParser, DataNormalizer

logger = logging.getLogger(__name__)


class TimeSeriesLoader:
    """时序数据加载器"""

    def __init__(self, db: KnowledgeBaseDB, data_dir: str):
        self.db = db
        self.data_dir = Path(data_dir)
        self.parser = ParquetParser(str(self.data_dir))
        self.normalizer = DataNormalizer()
        self.logger = logger

    def load_demand_timeseries(self, granularity: str = 'global') -> int:
        """
        加载技能需求时序数据

        Args:
            granularity: 数据粒度 ('global', 'company', 'occupation', 'region')

        Returns:
            加载的记录数量
        """
        self.logger.info(f"📈 加载技能需求时序数据 (粒度: {granularity})")

        try:
            demand_df = self.parser.parse_demand_data(granularity)
            proportion_df = self.parser.parse_proportion_data(granularity)

            time_columns = self.parser.get_time_columns(demand_df)

            if not time_columns:
                self.logger.warning("未找到时间列，跳过时序数据加载")
                return 0

            loaded_count = 0
            batch_size = 1000

            for idx, (_, demand_row) in enumerate(demand_df.iterrows()):
                skill_id = self._get_skill_id(demand_row, demand_df)

                if skill_id is None:
                    continue

                for time_col in time_columns:
                    demand_value = demand_row.get(time_col, 0)

                    proportion_value = None
                    if 'skill_id' in proportion_df.columns:
                        prop_row = proportion_df[proportion_df['skill_id'] == skill_id]
                        if not prop_row.empty:
                            proportion_value = prop_row.iloc[0].get(time_col)

                    time_period = self.normalizer.normalize_time_period(time_col)

                    if self.db.insert_skill_demand(
                        skill_id,
                        float(demand_value) if pd.notna(demand_value) else 0.0,
                        float(proportion_value) if proportion_value and pd.notna(proportion_value) else None,
                        time_period,
                        region=granularity if granularity != 'global' else 'global',
                        granularity=granularity
                    ):
                        loaded_count += 1

                if (idx + 1) % batch_size == 0:
                    self.logger.info(f"  已处理 {idx + 1} 个技能...")

            self.logger.info(f"✅ 成功加载 {loaded_count} 条时序记录")
            return loaded_count

        except Exception as e:
            self.logger.error(f"❌ 加载时序数据失败: {e}")
            return 0

    def _get_skill_id(self, row: pd.Series, df: pd.DataFrame) -> Optional[int]:
        """从行数据中提取技能ID"""
        if 'skill_id' in row.index:
            return int(row['skill_id'])

        if 'skill_id' in df.columns:
            return int(row['skill_id'])

        if df.index.name == 'skill_id':
            return int(df.index[idx]) if 'idx' in dir() else None

        for col in ['id', 'skill', 'name']:
            if col in row.index:
                try:
                    return int(row[col])
                except:
                    pass

        return None

    def aggregate_demand_by_period(self, start_period: str,
                                   end_period: str) -> pd.DataFrame:
        """
        按时间段聚合需求数据

        Args:
            start_period: 开始时间 (YYYY-MM)
            end_period: 结束时间 (YYYY-MM)

        Returns:
            聚合后的DataFrame
        """
        self.logger.info(f"📊 聚合需求数据: {start_period} 至 {end_period}")

        try:
            skills = self.db.get_all_skills()
            aggregated = []

            for skill in skills:
                trend = self.db.get_skill_demand_trend(
                    skill['skill_id'],
                    start_period,
                    end_period
                )

                if trend:
                    demand_values = [r['demand_value'] for r in trend]
                    proportion_values = [r['proportion_value'] for r in trend
                                        if r.get('proportion_value')]

                    aggregated.append({
                        'skill_id': skill['skill_id'],
                        'skill_name': skill['skill_name'],
                        'avg_demand': sum(demand_values) / len(demand_values) if demand_values else 0,
                        'max_demand': max(demand_values) if demand_values else 0,
                        'min_demand': min(demand_values) if demand_values else 0,
                        'avg_proportion': sum(proportion_values) / len(proportion_values) if proportion_values else 0,
                        'trend_count': len(trend)
                    })

            result_df = pd.DataFrame(aggregated)
            self.logger.info(f"✅ 聚合完成: {len(result_df)} 个技能")
            return result_df

        except Exception as e:
            self.logger.error(f"❌ 聚合数据失败: {e}")
            return pd.DataFrame()

    def calculate_demand_growth_rate(self, skill_id: int,
                                    recent_periods: int = 6) -> Optional[float]:
        """
        计算技能需求增长率

        Args:
            skill_id: 技能ID
            recent_periods: 最近周期数

        Returns:
            增长率 (百分比)
        """
        try:
            trend = self.db.get_skill_demand_trend(skill_id)

            if len(trend) < recent_periods:
                return None

            recent_values = [r['demand_value'] for r in trend[-recent_periods:]]
            earlier_values = [r['demand_value'] for r in trend[-2*recent_periods:-recent_periods]]

            if not earlier_values or sum(earlier_values) == 0:
                return None

            recent_avg = sum(recent_values) / len(recent_values)
            earlier_avg = sum(earlier_values) / len(earlier_values)

            growth_rate = ((recent_avg - earlier_avg) / earlier_avg) * 100

            return round(growth_rate, 2)

        except Exception as e:
            self.logger.error(f"❌ 计算增长率失败: {e}")
            return None

    def get_top_growing_skills(self, limit: int = 50) -> List[Dict]:
        """
        获取增长最快的技能

        Args:
            limit: 返回数量

        Returns:
            技能列表
        """
        self.logger.info(f"📈 获取增长最快的 {limit} 个技能")

        try:
            skills = self.db.get_all_skills()
            growth_rates = []

            for skill in skills:
                growth_rate = self.calculate_demand_growth_rate(skill['skill_id'])

                if growth_rate is not None:
                    growth_rates.append({
                        'skill_id': skill['skill_id'],
                        'skill_name': skill['skill_name'],
                        'growth_rate': growth_rate,
                        **skill
                    })

            growth_rates.sort(key=lambda x: x['growth_rate'], reverse=True)

            return growth_rates[:limit]

        except Exception as e:
            self.logger.error(f"❌ 获取增长技能失败: {e}")
            return []

    def get_trending_skills(self, recent_months: int = 3,
                          min_demand_threshold: float = 100) -> List[Dict]:
        """
        获取近期热门技能

        Args:
            recent_months: 最近的月份数
            min_demand_threshold: 最小需求阈值

        Returns:
            热门技能列表
        """
        self.logger.info(f"🔥 获取近期热门技能 (最近 {recent_months} 个月)")

        try:
            skills = self.db.get_all_skills()
            trending = []

            for skill in skills:
                trend = self.db.get_skill_demand_trend(skill['skill_id'])

                if len(trend) < recent_months:
                    continue

                recent_demand = sum(r['demand_value'] for r in trend[-recent_months:])

                if recent_demand >= min_demand_threshold:
                    trending.append({
                        'skill_id': skill['skill_id'],
                        'skill_name': skill['skill_name'],
                        'recent_demand': recent_demand,
                        'avg_demand': recent_demand / recent_months,
                        **skill
                    })

            trending.sort(key=lambda x: x['recent_demand'], reverse=True)

            return trending[:50]

        except Exception as e:
            self.logger.error(f"❌ 获取热门技能失败: {e}")
            return []
