"""
Agent工具注册器
统一管理和调度所有Agent工具
"""

import logging
from typing import Dict, List, Optional, Any
from .base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Agent工具注册器
    管理所有可用的工具，提供统一的调用接口
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = {}
        self.logger = logger

    def register(self, tool: BaseTool, category: Optional[str] = "general") -> None:
        """
        注册工具

        Args:
            tool: 工具实例
            category: 工具分类
        """
        if tool.name in self._tools:
            self.logger.warning(f"Tool {tool.name} already registered, overwriting")

        self._tools[tool.name] = tool

        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(tool.name)

        self.logger.info(f"Registered tool: {tool.name} in category: {category}")

    def register_all(self, tools: List[BaseTool], category: str = "general") -> None:
        """
        批量注册工具

        Args:
            tools: 工具列表
            category: 工具分类
        """
        for tool in tools:
            self.register(tool, category)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        获取工具

        Args:
            name: 工具名称

        Returns:
            BaseTool or None
        """
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[Dict]:
        """
        列出工具

        Args:
            category: 分类筛选

        Returns:
            工具列表
        """
        if category:
            tool_names = self._categories.get(category, [])
            return [
                {
                    "name": name,
                    "description": self._tools[name].description,
                    "schema": self._tools[name].get_schema()
                }
                for name in tool_names if name in self._tools
            ]

        return [
            {
                "name": name,
                "description": tool.description,
                "schema": tool.get_schema(),
                "category": self._get_tool_category(name)
            }
            for name, tool in self._tools.items()
        ]

    def _get_tool_category(self, tool_name: str) -> Optional[str]:
        """获取工具分类"""
        for category, tools in self._categories.items():
            if tool_name in tools:
                return category
        return None

    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """
        执行工具

        Args:
            tool_name: 工具名称
            **kwargs: 工具参数

        Returns:
            ToolResult
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}"
            )

        if not tool.enabled:
            return ToolResult(
                success=False,
                error=f"Tool disabled: {tool_name}"
            )

        try:
            result = await tool.execute(**kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Tool execution failed: {tool_name}, error: {e}")
            return ToolResult(
                success=False,
                error=str(e)
            )

    async def execute_chain(self, tool_sequence: List[Dict]) -> List[ToolResult]:
        """
        顺序执行工具链

        Args:
            tool_sequence: 工具调用序列 [{"tool": "tool_name", "params": {...}}, ...]

        Returns:
            执行结果列表
        """
        results = []
        context = {}

        for step in tool_sequence:
            tool_name = step.get("tool")
            params = step.get("params", {})

            result = await self.execute(tool_name, **params)

            context[tool_name] = result.data
            results.append(result)

            if not result.success:
                self.logger.warning(f"Tool {tool_name} failed, stopping chain")
                break

        return results

    def get_tools_by_capability(self, capability: str) -> List[BaseTool]:
        """
        根据能力获取工具

        Args:
            capability: 能力标识

        Returns:
            匹配的工具列表
        """
        capability_map = {
            "skill_normalize": ["normalize_skill"],
            "skill_related": ["get_related_skills"],
            "skill_recommend": ["get_skill_recommendations"],
            "skill_trend": ["get_skill_trend"],
            "match": ["calculate_match", "enhance_match"],
            "gap_analysis": ["get_skill_gap"],
            "parse_resume": ["parse_resume"],
            "parse_job": ["parse_job"],
            "extract_skills": ["extract_skills"]
        }

        tool_names = capability_map.get(capability, [])
        return [self._tools[name] for name in tool_names if name in self._tools]

    def get_statistics(self) -> Dict[str, Any]:
        """获取工具统计"""
        return {
            "total_tools": len(self._tools),
            "categories": {
                category: len(tools)
                for category, tools in self._categories.items()
            },
            "enabled_tools": sum(1 for t in self._tools.values() if t.enabled),
            "disabled_tools": sum(1 for t in self._tools.values() if not t.enabled)
        }

    def enable_tool(self, tool_name: str) -> bool:
        """启用工具"""
        tool = self.get_tool(tool_name)
        if tool:
            tool.enabled = True
            return True
        return False

    def disable_tool(self, tool_name: str) -> bool:
        """禁用工具"""
        tool = self.get_tool(tool_name)
        if tool:
            tool.enabled = False
            return True
        return False


_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """获取全局工具注册器"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
        _register_default_tools(_global_registry)
    return _global_registry


def _register_default_tools(registry: ToolRegistry):
    """注册默认工具"""
    from .skill_tools import (
        normalize_skill_tool,
        get_related_skills_tool,
        get_skill_recommendations_tool,
        get_skill_trend_tool
    )
    from .match_tools import (
        calculate_match_tool,
        enhance_match_tool,
        get_skill_gap_tool
    )
    from .parse_tools import (
        parse_resume_tool,
        parse_job_tool,
        extract_skills_tool
    )

    registry.register(normalize_skill_tool, "skill")
    registry.register(get_related_skills_tool, "skill")
    registry.register(get_skill_recommendations_tool, "skill")
    registry.register(get_skill_trend_tool, "skill")

    registry.register(calculate_match_tool, "match")
    registry.register(enhance_match_tool, "match")
    registry.register(get_skill_gap_tool, "match")

    registry.register(parse_resume_tool, "parse")
    registry.register(parse_job_tool, "parse")
    registry.register(extract_skills_tool, "parse")
