"""
Parquet 文件解析器
用于解析 Job-SDF 数据集中的 Parquet 格式文件
"""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
import os

logger = logging.getLogger(__name__)


class ParquetParser:
    """Parquet文件解析器"""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.logger = logger

    def parse_demand_data(self, granularity: str = 'global') -> pd.DataFrame:
        """
        解析技能需求数据

        Args:
            granularity: 数据粒度 ('global', 'company', 'occupation', 'region')

        Returns:
            包含技能需求数据的DataFrame
        """
        demand_file = self.data_dir / "demand" / f"{granularity}.parquet"

        if not demand_file.exists():
            demand_dir = self.data_dir / "demand"
            if demand_dir.exists():
                parquet_files = list(demand_dir.glob("*.parquet"))
                if parquet_files:
                    demand_file = parquet_files[0]
                    self.logger.info(f"使用文件: {demand_file}")

        if not demand_file.exists():
            raise FileNotFoundError(f"需求数据文件不存在: {demand_file}")

        try:
            df = pd.read_parquet(demand_file)
            self.logger.info(f"✅ 成功加载需求数据: {len(df)} 行")
            return df
        except Exception as e:
            self.logger.error(f"❌ 解析需求数据失败: {e}")
            raise

    def parse_proportion_data(self, granularity: str = 'global') -> pd.DataFrame:
        """
        解析技能需求占比数据

        Args:
            granularity: 数据粒度

        Returns:
            包含技能需求占比的DataFrame
        """
        proportion_file = self.data_dir / "proportion" / f"{granularity}.parquet"

        if not proportion_file.exists():
            proportion_dir = self.data_dir / "proportion"
            if proportion_dir.exists():
                parquet_files = list(proportion_dir.glob("*.parquet"))
                if parquet_files:
                    proportion_file = parquet_files[0]
                    self.logger.info(f"使用文件: {proportion_file}")

        if not proportion_file.exists():
            raise FileNotFoundError(f"占比数据文件不存在: {proportion_file}")

        try:
            df = pd.read_parquet(proportion_file)
            self.logger.info(f"✅ 成功加载占比数据: {len(df)} 行")
            return df
        except Exception as e:
            self.logger.error(f"❌ 解析占比数据失败: {e}")
            raise

    def parse_graph_data(self, graph_type: str = 'co_occurrence') -> pd.DataFrame:
        """
        解析技能关系图数据

        Args:
            graph_type: 图类型 ('co_occurrence', 'similarity')

        Returns:
            包含技能关系的DataFrame
        """
        graph_file = self.data_dir / "graph" / f"{graph_type}.parquet"

        if not graph_file.exists():
            graph_dir = self.data_dir / "graph"
            if graph_dir.exists():
                parquet_files = list(graph_dir.glob("*.parquet"))
                if parquet_files:
                    graph_file = parquet_files[0]
                    self.logger.info(f"使用文件: {graph_file}")

        if not graph_file.exists():
            raise FileNotFoundError(f"图数据文件不存在: {graph_file}")

        try:
            df = pd.read_parquet(graph_file)
            self.logger.info(f"✅ 成功加载图数据: {len(df)} 行")
            return df
        except Exception as e:
            self.logger.error(f"❌ 解析图数据失败: {e}")
            raise

    def parse_all_demand_files(self) -> List[pd.DataFrame]:
        """解析所有需求数据文件"""
        demand_dir = self.data_dir / "demand"

        if not demand_dir.exists():
            self.logger.warning(f"需求目录不存在: {demand_dir}")
            return []

        parquet_files = list(demand_dir.glob("*.parquet"))
        dfs = []

        for file_path in parquet_files:
            try:
                df = pd.read_parquet(file_path)
                df['source_file'] = file_path.name
                dfs.append(df)
                self.logger.info(f"  已加载: {file_path.name}")
            except Exception as e:
                self.logger.error(f"  加载失败 {file_path.name}: {e}")

        return dfs

    def get_time_columns(self, df: pd.DataFrame) -> List[str]:
        """
        从DataFrame中提取时间列

        Args:
            df: 数据DataFrame

        Returns:
            时间列列表
        """
        time_columns = []

        for col in df.columns:
            col_str = str(col)
            if self._is_time_column(col_str):
                time_columns.append(col_str)

        if not time_columns:
            if isinstance(df.index, pd.DatetimeIndex):
                time_columns = [df.index.name or 'time']
            elif hasattr(df.index, 'strftime'):
                time_columns = ['time']

        return sorted(time_columns)

    def _is_time_column(self, column_name: str) -> bool:
        """判断列是否为时间列"""
        time_patterns = [
            r'\d{4}-\d{2}',
            r'\d{4}_\d{2}',
            r'\d{4}年\d{1,2}月',
            r'month_\d+',
            r'time_period_',
            r'date_',
            r'period_'
        ]

        import re
        for pattern in time_patterns:
            if re.search(pattern, column_name):
                return True

        return False

    def get_skill_ids_from_dataframe(self, df: pd.DataFrame) -> List[Any]:
        """
        从DataFrame提取技能ID列表

        Args:
            df: 数据DataFrame

        Returns:
            技能ID列表
        """
        if 'skill_id' in df.columns:
            return df['skill_id'].unique().tolist()

        if df.index.name == 'skill_id' or 'skill_id' in df.index.names:
            return df.index.unique().tolist()

        for col in df.columns[:5]:
            if df[col].dtype in ['int64', 'int32', 'str', 'object']:
                return df[col].unique().tolist()[:1000]

        return []

    def merge_demand_and_proportion(self,
                                   demand_df: pd.DataFrame,
                                   proportion_df: pd.DataFrame) -> pd.DataFrame:
        """
        合并需求数据和占比数据

        Args:
            demand_df: 需求DataFrame
            proportion_df: 占比DataFrame

        Returns:
            合并后的DataFrame
        """
        if 'skill_id' in demand_df.columns and 'skill_id' in proportion_df.columns:
            merged = pd.merge(demand_df, proportion_df,
                            on='skill_id',
                            how='outer',
                            suffixes=('_demand', '_proportion'))
        else:
            merged = pd.concat([demand_df, proportion_df], axis=1)

        self.logger.info(f"✅ 数据合并完成: {len(merged)} 行")
        return merged

    def convert_to_timeseries_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        将宽格式数据转换为长格式时序数据

        Args:
            df: 宽格式DataFrame

        Returns:
            长格式时序DataFrame
        """
        time_columns = self.get_time_columns(df)

        if not time_columns:
            return df

        id_columns = [col for col in df.columns if col not in time_columns]

        df_long = df.melt(
            id_vars=id_columns if id_columns else None,
            value_vars=time_columns,
            var_name='time_period',
            value_name='demand_value'
        )

        self.logger.info(f"✅ 转换为时序格式: {len(df_long)} 行")
        return df_long
