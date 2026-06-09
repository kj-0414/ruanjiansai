"""
数据标准化模块
负责技能名称、别名等数据的标准化处理
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DataNormalizer:
    """数据标准化类"""

    def __init__(self):
        self.skill_aliases = {}
        self.skill_categories = self._get_default_categories()
        self.logger = logger

    def normalize_skill_name(self, raw_name: str) -> str:
        """
        标准化技能名称

        Args:
            raw_name: 原始技能名称

        Returns:
            标准化后的技能名称
        """
        if not raw_name:
            return ""

        normalized = raw_name.strip()

        normalized = re.sub(r'\s+', ' ', normalized)

        normalized = normalized.title()

        normalization_rules = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'python': 'Python',
            'java': 'Java',
            'golang': 'Go',
            'nodejs': 'Node.js',
            'node.js': 'Node.js',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'kubernetes': 'Kubernetes',
            'docker': 'Docker',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'reactjs': 'React',
            'vuejs': 'Vue',
            'angularjs': 'Angular',
            'aws': 'AWS',
            'gcp': 'GCP',
            'mysql': 'MySQL',
            'redis': 'Redis',
            'linux': 'Linux',
            'git': 'Git',
            'kubernetes': 'Kubernetes'
        }

        normalized_lower = normalized.lower()
        if normalized_lower in normalization_rules:
            normalized = normalization_rules[normalized_lower]

        return normalized

    def detect_category(self, skill_name: str) -> Optional[str]:
        """
        根据技能名称推断类别

        Args:
            skill_name: 技能名称

        Returns:
            技能类别
        """
        skill_lower = skill_name.lower()

        category_keywords = {
            '编程语言': ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r语言', 'matlab'],
            '前端技术': ['html', 'css', 'react', 'vue', 'angular', 'jquery', 'bootstrap', 'sass', 'less', 'webpack', 'vite', 'next.js', 'nuxt'],
            '后端框架': ['django', 'flask', 'fastapi', 'spring', 'springboot', 'express', 'koa', 'nestjs', 'rails', 'laravel', '.net'],
            '数据库': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'sqlite', 'oracle', 'sql server', 'dynamodb'],
            '大数据': ['hadoop', 'spark', 'kafka', 'flink', 'hive', 'hbase', 'storm', 'mapreduce'],
            '机器学习': ['tensorflow', 'pytorch', 'keras', 'scikit-learn', 'xgboost', 'lightgbm', 'caffe', 'mxnet'],
            '深度学习': ['cnn', 'rnn', 'lstm', 'gru', 'gan', 'transformer', 'bert', 'gpt'],
            '容器技术': ['docker', 'kubernetes', 'helm', 'istio', 'containerd'],
            '云服务': ['aws', 'azure', 'gcp', 'aliyun', 'tencent cloud', '华为云'],
            'DevOps工具': ['jenkins', 'gitlab', 'github', 'jira', 'ansible', 'terraform', 'puppet'],
            '版本控制': ['git', 'svn', 'mercurial'],
            '操作系统': ['linux', 'windows', 'unix', 'macos', 'ubuntu', 'centos'],
            '网络技术': ['http', 'tcp', 'udp', 'dns', 'cdn', 'nginx', 'apache'],
            '移动开发': ['ios', 'android', 'react native', 'flutter', 'swift', 'objective-c', 'kotlin'],
            '数据可视化': ['echarts', 'd3.js', 'tableau', 'powerbi', 'grafana', 'kibana']
        }

        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in skill_lower:
                    return category

        return '其他'

    def _get_default_categories(self) -> Dict[str, List[str]]:
        """获取默认技能分类"""
        return {
            '编程语言': ['Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'Ruby', 'PHP'],
            '前端技术': ['React', 'Vue', 'Angular', 'HTML', 'CSS', 'SASS', 'Webpack', 'Vite'],
            '后端框架': ['Django', 'Flask', 'Spring', 'Express', 'FastAPI', 'NestJS'],
            '数据库': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch'],
            '大数据': ['Hadoop', 'Spark', 'Kafka', 'Flink', 'Hive'],
            '机器学习': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'XGBoost'],
            '容器技术': ['Docker', 'Kubernetes', 'Helm'],
            '云服务': ['AWS', 'Azure', 'GCP', '阿里云'],
            'DevOps工具': ['Jenkins', 'GitLab', 'Ansible', 'Terraform']
        }

    def normalize_skill_aliases(self, skill_name: str) -> List[str]:
        """
        获取技能的所有标准化别名

        Args:
            skill_name: 技能名称

        Returns:
            别名列表
        """
        normalized = self.normalize_skill_name(skill_name)
        aliases = [normalized, normalized.lower()]

        common_aliases = {
            'JavaScript': ['js', 'javascript', 'ecmascript'],
            'TypeScript': ['ts', 'typescript'],
            'Python': ['py', 'python', 'python3'],
            'React': ['react', 'reactjs', 'react.js'],
            'Vue': ['vue', 'vuejs', 'vue.js', 'vue3'],
            'Node.js': ['node', 'nodejs', 'node.js'],
            'MySQL': ['mysql', 'mysql数据库'],
            'PostgreSQL': ['postgresql', 'postgres', 'pg'],
            'MongoDB': ['mongodb', 'mongo', 'nosql'],
            'Docker': ['docker', 'docker容器'],
            'Kubernetes': ['kubernetes', 'k8s', 'k8s容器编排'],
            'TensorFlow': ['tensorflow', 'tf', 'tf框架'],
            'PyTorch': ['pytorch', 'torch', 'pytorch框架'],
            'Git': ['git', 'git版本控制'],
            'AWS': ['aws', 'amazon web services', '亚马逊云']
        }

        if normalized in common_aliases:
            aliases.extend(common_aliases[normalized])

        return list(set(aliases))

    def parse_skill_level(self, level_str: str) -> int:
        """
        解析技能难度等级

        Args:
            level_str: 等级描述字符串

        Returns:
            等级数值 (1-5)
        """
        if not level_str:
            return 3

        level_str = level_str.lower()

        if any(word in level_str for word in ['初级', '基础', '入门', 'basic', 'beginner', 'entry']):
            return 1
        elif any(word in level_str for word in ['中级', '进阶', 'intermediate', 'advanced']):
            return 3
        elif any(word in level_str for word in ['高级', '资深', 'expert', 'senior']):
            return 5

        if level_str.isdigit():
            return min(max(int(level_str), 1), 5)

        return 3

    def normalize_time_period(self, period: str) -> str:
        """
        标准化时间周期格式

        Args:
            period: 原始时间周期字符串

        Returns:
            标准化的周期字符串 (YYYY-MM)
        """
        period = period.strip()

        patterns = [
            (r'(\d{4})[年/-](\d{1,2})', r'\1-\2'),
            (r'(\d{4})(\d{2})', r'\1-\2'),
            (r'month_(\d+)', lambda m: self._month_offset_to_date(int(m.group(1)))),
            (r'period_(\d+)', lambda m: self._month_offset_to_date(int(m.group(1))))
        ]

        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, period)
            if result != period:
                return result

        return period

    def _month_offset_to_date(self, offset: int) -> str:
        """将月份偏移量转换为日期"""
        base_year = 2018
        year = base_year + offset // 12
        month = offset % 12 + 1
        return f"{year}-{month:02d}"

    def validate_skill_data(self, skill_data: Dict) -> Tuple[bool, List[str]]:
        """
        验证技能数据的完整性

        Args:
            skill_data: 技能数据字典

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        if not skill_data.get('skill_name'):
            errors.append("技能名称不能为空")

        if 'difficulty_level' in skill_data:
            level = skill_data['difficulty_level']
            if not isinstance(level, int) or level < 1 or level > 5:
                errors.append("技能等级应在1-5之间")

        if 'weight' in skill_data:
            weight = skill_data['weight']
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                errors.append("权重应在0-1之间")

        return len(errors) == 0, errors

    def clean_text(self, text: str) -> str:
        """
        清理文本数据

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text:
            return ""

        text = text.strip()

        text = re.sub(r'\s+', ' ', text)

        text = re.sub(r'[^\w\s\u4e00-\u9fa5.-]', '', text)

        return text

    def normalize_skill_set(self, skills: List[str]) -> List[str]:
        """
        标准化技能集合（去重、清理）

        Args:
            skills: 原始技能列表

        Returns:
            标准化后的技能列表
        """
        normalized_skills = []

        for skill in skills:
            if not skill:
                continue

            normalized = self.normalize_skill_name(skill)

            if normalized and normalized not in normalized_skills:
                normalized_skills.append(normalized)

        return normalized_skills

    def get_skill_fingerprint(self, skill_name: str) -> str:
        """
        获取技能指纹（用于快速匹配）

        Args:
            skill_name: 技能名称

        Returns:
            指纹字符串
        """
        normalized = self.normalize_skill_name(skill_name)
        return normalized.lower().replace(' ', '').replace('.', '')
