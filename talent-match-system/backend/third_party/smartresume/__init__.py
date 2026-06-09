"""
SmartResume集成模块
使用项目现有的LLM引擎进行简历解析
"""

import os
import sys

# 将SmartResume源码路径添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
smartresume_path = current_dir
sys.path.insert(0, smartresume_path)

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SmartResumeParser:
    """SmartResume简历解析器封装"""

    def __init__(self):
        """初始化SmartResume解析器"""
        self.parser = None
        self._initialized = False

    def _initialize(self):
        """延迟初始化SmartResume"""
        if self._initialized:
            return

        try:
            from smartresume.backend.resume_analyzer import ResumeAnalyzer

            config_path = os.path.join(current_dir, 'configs', 'config.yaml')
            self.parser = ResumeAnalyzer(config_path=config_path)
            self._initialized = True
            logger.info("SmartResume parser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SmartResume: {e}")
            self.parser = None
            self._initialized = True

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件

        Args:
            file_path: 简历文件路径

        Returns:
            解析后的结构化数据
        """
        self._initialize()

        if self.parser is None:
            raise RuntimeError("SmartResume parser not available")

        try:
            result = self.parser.analyze(file_path)
            return self._convert_result(result)
        except Exception as e:
            logger.error(f"Failed to parse resume: {e}")
            raise

    def _convert_result(self, result: Any) -> Dict[str, Any]:
        """转换SmartResume结果为统一格式"""
        try:
            return {
                "name": result.get("name", "未提供"),
                "phone": result.get("phone", ""),
                "email": result.get("email", ""),
                "education": result.get("education", "未提供"),
                "experience_years": result.get("experience", "未提供"),
                "skills": result.get("skills", []),
                "work_experience": result.get("work_experience", []),
                "education_history": result.get("education_history", []),
                "self_evaluation": result.get("summary", ""),
                "highlights": result.get("highlights", []),
                "source": "smartresume",
                "confidence": 0.93
            }
        except Exception as e:
            logger.error(f"Failed to convert result: {e}")
            return {}

    def parse_text(self, text: str) -> Dict[str, Any]:
        """
        解析文本内容（不依赖文件）

        Args:
            text: 简历文本内容

        Returns:
            解析后的结构化数据
        """
        self._initialize()

        if self.parser is None:
            raise RuntimeError("SmartResume parser not available")

        try:
            result = self.parser.analyze_text(text)
            return self._convert_result(result)
        except Exception as e:
            logger.error(f"Failed to parse text: {e}")
            raise


# 创建全局解析器实例
_parser: Optional[SmartResumeParser] = None


def get_parser() -> SmartResumeParser:
    """获取SmartResume解析器单例"""
    global _parser
    if _parser is None:
        _parser = SmartResumeParser()
    return _parser


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    解析简历文件的便捷函数

    Args:
        file_path: 简历文件路径

    Returns:
        解析后的结构化数据
    """
    parser = get_parser()
    return parser.parse(file_path)


def parse_resume_text(text: str) -> Dict[str, Any]:
    """
    解析简历文本的便捷函数

    Args:
        text: 简历文本内容

    Returns:
        解析后的结构化数据
    """
    parser = get_parser()
    return parser.parse_text(text)
