"""
Agent工具基础类
定义工具的接口和通用结构
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None
    execution_time: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }

    def __str__(self) -> str:
        if self.success:
            return f"ToolResult(success=True, data={self.data})"
        else:
            return f"ToolResult(success=False, error={self.error})"


class BaseTool(ABC):
    """
    Agent工具基类
    所有工具都应该继承此类并实现 execute 方法
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Optional[List[Dict]] = None,
        enabled: bool = True
    ):
        self.name = name
        self.description = description
        self.parameters = parameters or []
        self.enabled = enabled
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            ToolResult: 执行结果
        """
        pass

    def validate_parameters(self, params: Dict) -> bool:
        """
        验证参数

        Args:
            params: 参数字典

        Returns:
            bool: 是否有效
        """
        required_params = [p["name"] for p in self.parameters if p.get("required", False)]

        for param in required_params:
            if param not in params:
                self.logger.error(f"Missing required parameter: {param}")
                return False

        return True

    def get_schema(self) -> Dict:
        """
        获取工具的JSON Schema

        Returns:
            Dict: 工具schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p["name"]: {
                        "type": p.get("type", "string"),
                        "description": p.get("description", ""),
                        "required": p.get("required", False)
                    }
                    for p in self.parameters
                }
            }
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, enabled={self.enabled})"


class ToolDecorator:
    """
    工具装饰器
    用于添加日志、缓存、限流等功能
    """

    @staticmethod
    def with_logging(tool: BaseTool) -> BaseTool:
        """添加日志装饰器"""
        original_execute = tool.execute

        async def logged_execute(**kwargs):
            start_time = datetime.now()
            tool.logger.info(f"Executing tool: {tool.name} with params: {kwargs}")

            result = await original_execute(**kwargs)

            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time

            tool.logger.info(f"Tool {tool.name} completed in {execution_time:.2f}s")

            return result

        tool.execute = logged_execute
        return tool

    @staticmethod
    def with_cache(ttl: int = 300):
        """
        添加缓存装饰器

        Args:
            ttl: 缓存有效期（秒）
        """
        cache = {}

        def decorator(tool: BaseTool) -> BaseTool:
            original_execute = tool.execute

            async def cached_execute(**kwargs):
                cache_key = json.dumps(kwargs, sort_keys=True)

                if cache_key in cache:
                    cached_result, cached_time = cache[cache_key]
                    if (datetime.now() - cached_time).total_seconds() < ttl:
                        tool.logger.info(f"Cache hit for tool: {tool.name}")
                        return cached_result

                result = await original_execute(**kwargs)
                cache[cache_key] = (result, datetime.now())

                return result

            tool.execute = cached_execute
            return tool

        return decorator

    @staticmethod
    def with_retry(max_retries: int = 3, retry_delay: float = 1.0):
        """
        添加重试装饰器

        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        def decorator(tool: BaseTool) -> BaseTool:
            original_execute = tool.execute

            async def retry_execute(**kwargs):
                import asyncio

                for attempt in range(max_retries):
                    try:
                        result = await original_execute(**kwargs)
                        if result.success:
                            return result
                    except Exception as e:
                        tool.logger.warning(f"Attempt {attempt + 1} failed: {e}")

                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))

                return await original_execute(**kwargs)

            tool.execute = retry_execute
            return tool

        return decorator


class AsyncToolWrapper:
    """
    异步工具包装器
    将同步工具包装为异步工具
    """

    def __init__(self, tool: BaseTool):
        self.tool = tool

    async def execute(self, **kwargs) -> ToolResult:
        """异步执行工具"""
        import asyncio

        def sync_execute():
            return asyncio.run(self.tool.execute(**kwargs))

        loop = asyncio.get_event_loop()
        if loop.is_running():
            future = loop.run_in_executor(None, sync_execute)
            return await future
        else:
            return await asyncio.to_thread(sync_execute)
