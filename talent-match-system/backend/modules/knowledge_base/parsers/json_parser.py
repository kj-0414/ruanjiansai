"""
JSON 文件解析器
用于解析 Job-SDF 数据集中的 JSON 格式文件
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class JSONParser:
    """JSON文件解析器"""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.logger = logger

    def parse_structural_breaks(self) -> List[str]:
        """
        解析结构突变技能索引

        Returns:
            结构突变技能ID列表
        """
        breaks_file = self.data_dir / "structural_breaks_index" / "company.json"

        if not breaks_file.exists():
            breaks_dir = self.data_dir / "structural_breaks_index"
            if breaks_dir.exists():
                json_files = list(breaks_dir.glob("*.json"))
                if json_files:
                    breaks_file = json_files[0]

        if not breaks_file.exists():
            self.logger.warning(f"结构突变索引文件不存在")
            return []

        try:
            with open(breaks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                skills = data
            elif isinstance(data, dict):
                skills = data.get('skills', data.get('structural_breaks', []))
            else:
                skills = []

            self.logger.info(f"✅ 加载 {len(skills)} 个结构突变技能")
            return [str(s) for s in skills]

        except Exception as e:
            self.logger.error(f"❌ 解析结构突变索引失败: {e}")
            return []

    def parse_low_frequency(self) -> List[str]:
        """
        解析低频技能索引

        Returns:
            低频技能ID列表
        """
        low_freq_file = self.data_dir / "low_frequency_index" / "company.json"

        if not low_freq_file.exists():
            low_freq_dir = self.data_dir / "low_frequency_index"
            if low_freq_dir.exists():
                json_files = list(low_freq_dir.glob("*.json"))
                if json_files:
                    low_freq_file = json_files[0]

        if not low_freq_file.exists():
            self.logger.warning(f"低频技能索引文件不存在")
            return []

        try:
            with open(low_freq_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                skills = data
            elif isinstance(data, dict):
                skills = data.get('skills', data.get('low_frequency', []))
            else:
                skills = []

            self.logger.info(f"✅ 加载 {len(skills)} 个低频技能")
            return [str(s) for s in skills]

        except Exception as e:
            self.logger.error(f"❌ 解析低频技能索引失败: {e}")
            return []

    def parse_skill_metadata(self, metadata_file: str) -> Dict[str, Any]:
        """
        解析技能元数据文件

        Args:
            metadata_file: 元数据文件名

        Returns:
            技能元数据字典
        """
        file_path = self.data_dir / metadata_file

        if not file_path.exists():
            self.logger.warning(f"元数据文件不存在: {metadata_file}")
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            self.logger.info(f"✅ 加载元数据: {len(metadata)} 条")
            return metadata

        except Exception as e:
            self.logger.error(f"❌ 解析元数据失败: {e}")
            return {}

    def parse_occupation_mapping(self) -> List[Dict[str, Any]]:
        """
        解析职业分类映射

        Returns:
            职业分类列表
        """
        mapping_file = self.data_dir / "occupation_mapping.json"

        if not mapping_file.exists():
            self.logger.warning(f"职业映射文件不存在，使用默认分类")
            return self._get_default_occupations()

        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                occupations = json.load(f)

            self.logger.info(f"✅ 加载 {len(occupations)} 个职业分类")
            return occupations

        except Exception as e:
            self.logger.error(f"❌ 解析职业映射失败: {e}")
            return self._get_default_occupations()

    def _get_default_occupations(self) -> List[Dict[str, Any]]:
        """获取默认职业分类"""
        return [
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0101",
                "level2_name": "前端开发",
                "key_skills": ["JavaScript", "TypeScript", "React", "Vue", "Angular"],
                "demand_level": "high"
            },
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0102",
                "level2_name": "后端开发",
                "key_skills": ["Java", "Python", "Go", "Node.js", "Spring"],
                "demand_level": "high"
            },
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0103",
                "level2_name": "全栈开发",
                "key_skills": ["JavaScript", "Python", "React", "Node.js", "SQL"],
                "demand_level": "high"
            },
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0104",
                "level2_name": "移动端开发",
                "key_skills": ["Swift", "Kotlin", "React Native", "Flutter", "iOS", "Android"],
                "demand_level": "medium"
            },
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0105",
                "level2_name": "数据工程师",
                "key_skills": ["Python", "SQL", "Spark", "Hadoop", "Kafka"],
                "demand_level": "high"
            },
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0106",
                "level2_name": "算法工程师",
                "key_skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning"],
                "demand_level": "high"
            },
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0107",
                "level2_name": "DevOps工程师",
                "key_skills": ["Docker", "Kubernetes", "Jenkins", "AWS", "Linux"],
                "demand_level": "high"
            },
            {
                "level1_code": "L1-01",
                "level1_name": "计算机软件",
                "level2_code": "L2-0108",
                "level2_name": "测试工程师",
                "key_skills": ["Selenium", "JUnit", "Python", "Postman", "Jenkins"],
                "demand_level": "medium"
            },
            {
                "level1_code": "L1-02",
                "level1_name": "计算机硬件",
                "level2_code": "L2-0201",
                "level2_name": "嵌入式开发",
                "key_skills": ["C", "C++", "RTOS", "ARM", "Linux"],
                "demand_level": "medium"
            },
            {
                "level1_code": "L1-03",
                "level1_name": "互联网",
                "level2_code": "L2-0301",
                "level2_name": "产品经理",
                "key_skills": ["产品设计", "需求分析", "项目管理", "数据分析", "Axure"],
                "demand_level": "high"
            },
            {
                "level1_code": "L1-03",
                "level1_name": "互联网",
                "level2_code": "L2-0302",
                "level2_name": "UI/UX设计",
                "key_skills": ["Figma", "Sketch", "Adobe XD", "Photoshop", "UI设计"],
                "demand_level": "medium"
            },
            {
                "level1_code": "L1-04",
                "level1_name": "电子技术",
                "level2_code": "L2-0401",
                "level2_name": "硬件工程师",
                "key_skills": ["电路设计", "PCB", "FPGA", "Verilog", "VHDL"],
                "demand_level": "medium"
            }
        ]

    def parse_skill_aliases(self) -> Dict[str, List[str]]:
        """
        解析技能别名映射

        Returns:
            技能别名字典 {标准名称: [别名列表]}
        """
        aliases_file = self.data_dir / "skill_aliases.json"

        if not aliases_file.exists():
            return self._get_common_skill_aliases()

        try:
            with open(aliases_file, 'r', encoding='utf-8') as f:
                aliases = json.load(f)

            self.logger.info(f"✅ 加载 {len(aliases)} 个技能别名映射")
            return aliases

        except Exception as e:
            self.logger.error(f"❌ 解析技能别名失败: {e}")
            return self._get_common_skill_aliases()

    def _get_common_skill_aliases(self) -> Dict[str, List[str]]:
        """获取常见技能别名"""
        return {
            "Python": ["python", "py", "Python3", "python3"],
            "JavaScript": ["javascript", "js", "JS", "JavaScript ES6"],
            "TypeScript": ["typescript", "ts", "TS"],
            "Java": ["java", "Java SE", "Java EE"],
            "Go": ["go", "golang", "Golang"],
            "Rust": ["rust", "Rust语言"],
            "React": ["react", "React.js", "ReactJS"],
            "Vue": ["vue", "Vue.js", "VueJS", "Vue3"],
            "Angular": ["angular", "Angular.js", "AngularJS"],
            "Node.js": ["node", "nodejs", "Node", "NodeJS"],
            "Machine Learning": ["ml", "ML", "机器学习"],
            "Deep Learning": ["dl", "DL", "深度学习"],
            "Artificial Intelligence": ["ai", "AI", "人工智能"],
            "MySQL": ["mysql", "MySql", "my-sql"],
            "PostgreSQL": ["postgresql", "postgres", "Postgres"],
            "MongoDB": ["mongodb", "mongo", "Mongo"],
            "Redis": ["redis", "Redis缓存"],
            "Docker": ["docker", "Docker容器"],
            "Kubernetes": ["kubernetes", "k8s", "K8s"],
            "Git": ["git", "Git版本控制"],
            "AWS": ["aws", "Amazon Web Services"],
            "Azure": ["azure", "Microsoft Azure"],
            "GCP": ["gcp", "Google Cloud Platform"]
        }

    def save_json(self, data: Any, filename: str) -> bool:
        """
        保存数据为JSON文件

        Args:
            data: 要保存的数据
            filename: 文件名

        Returns:
            是否保存成功
        """
        try:
            file_path = self.data_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"✅ 数据已保存到: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ 保存JSON失败: {e}")
            return False
