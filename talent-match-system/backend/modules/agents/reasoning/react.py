"""
ReAct (Reasoning + Acting) 推理框架
实现思考-行动循环
"""

from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ActionStatus(Enum):
    """行动状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    FINISHED = "finished"


@dataclass
class ReActStep:
    """ReAct推理步骤"""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict] = None
    observation: Optional[str] = None
    status: ActionStatus = ActionStatus.PENDING
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "step_number": self.step_number,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "status": self.status.value,
            "error": self.error,
            "timestamp": self.timestamp
        }


class ToolExecutor:
    """工具执行器接口"""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable):
        """注册工具"""
        self.tools[name] = func

    async def execute(self, tool_name: str, **kwargs) -> Any:
        """执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool_func = self.tools[tool_name]

        if callable(tool_func):
            result = tool_func(**kwargs)
            if hasattr(result, '__await__'):
                return await result
            return result

        raise ValueError(f"Tool is not callable: {tool_name}")


class ReActAgent:
    """
    ReAct推理Agent
    实现: Thought -> Action -> Observation -> Thought 循环
    """

    def __init__(
        self,
        llm_client=None,
        max_iterations: int = 10,
        tool_executor: Optional[ToolExecutor] = None
    ):
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.tool_executor = tool_executor or ToolExecutor()
        self.steps: List[ReActStep] = []
        self.logger = logger

        self.tools_schema = []

    def register_tools(self, tools: List[Any]):
        """注册工具列表"""
        for tool in tools:
            if hasattr(tool, 'name') and hasattr(tool, 'execute'):
                async def wrapper(**kwargs):
                    return await tool.execute(**kwargs)

                self.tool_executor.register_tool(tool.name, wrapper)
                self.tools_schema.append(tool.get_schema())

    def _format_tools_description(self) -> str:
        """格式化工具描述"""
        if not self.tools_schema:
            return "No tools available."

        descriptions = []
        for tool in self.tools_schema:
            desc = f"\n{tool['name']}: {tool['description']}"
            params = tool.get('parameters', {}).get('properties', {})
            if params:
                desc += "\n  Parameters:"
                for param_name, param_info in params.items():
                    desc += f"\n    - {param_name}: {param_info.get('description', '')}"
            descriptions.append(desc)

        return "\n".join(descriptions)

    def _create_react_prompt(self, question: str, context: str = "") -> str:
        """创建ReAct提示"""
        tools_desc = self._format_tools_description()

        prompt = f"""You are a HR assistant that helps with resume-job matching using ReAct (Reasoning + Acting).

Question: {question}
{context}

You have access to the following tools:
{tools_desc}

Follow this format exactly:
Thought: [your reasoning about what to do]
Action: [the name of the tool to use, e.g., normalize_skill]
Action Input: [the input to the tool as a JSON object]
Observation: [the result of the action]

When you have enough information to answer, use this format instead:
Thought: [your final reasoning]
Action: finish
Action Input: {{"answer": "your final answer here"}}

Begin!"""

        return prompt

    async def think(self, question: str, context: str = "") -> Dict[str, Any]:
        """
        执行ReAct推理

        Args:
            question: 问题
            context: 上下文

        Returns:
            推理结果
        """
        self.steps = []
        self.logger.info(f"Starting ReAct reasoning for: {question}")

        for iteration in range(self.max_iterations):
            thought = ""
            action = None
            action_input = {}
            observation = None
            status = ActionStatus.RUNNING

            prompt = self._create_react_prompt(question, context)

            if self.llm_client:
                try:
                    response = await self._call_llm(prompt)
                    parsed = self._parse_llm_response(response)

                    thought = parsed.get("thought", "")
                    action = parsed.get("action")
                    action_input = parsed.get("action_input", {})

                except Exception as e:
                    self.logger.error(f"LLM call failed: {e}")
                    thought = f"Error in LLM call: {e}"
                    status = ActionStatus.FAILED
                    break

            step = ReActStep(
                step_number=iteration + 1,
                thought=thought,
                action=action,
                action_input=action_input,
                status=status
            )

            if action == "finish":
                step.status = ActionStatus.FINISHED
                step.observation = action_input.get("answer", "")
                self.steps.append(step)
                break

            if action:
                try:
                    observation = await self.tool_executor.execute(action, **action_input)
                    step.observation = str(observation)
                    step.status = ActionStatus.SUCCESS

                    context += f"\nObservation: {observation}"

                except Exception as e:
                    step.error = str(e)
                    step.status = ActionStatus.FAILED
                    self.logger.error(f"Tool execution failed: {e}")

            self.steps.append(step)

            if step.status == ActionStatus.FAILED:
                break

        final_answer = ""
        for step in reversed(self.steps):
            if step.action == "finish":
                final_answer = step.observation or ""
                break

        return {
            "question": question,
            "answer": final_answer,
            "steps": [s.to_dict() for s in self.steps],
            "total_steps": len(self.steps),
            "success": any(s.status == ActionStatus.SUCCESS for s in self.steps)
        }

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        if self.llm_client:
            response = self.llm_client.chat(prompt)
            return response if isinstance(response, str) else str(response)
        return ""

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        result = {
            "thought": "",
            "action": None,
            "action_input": {}
        }

        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Thought:'):
                result["thought"] = line[8:].strip()
            elif line.startswith('Action:'):
                result["action"] = line[7:].strip()
            elif line.startswith('Action Input:'):
                try:
                    json_str = line[13:].strip()
                    if json_str.startswith('{') and json_str.endswith('}'):
                        import json
                        result["action_input"] = json.loads(json_str)
                except:
                    pass

        return result

    def get_reasoning_trace(self) -> List[Dict]:
        """获取推理轨迹"""
        return [s.to_dict() for s in self.steps]

    def reset(self):
        """重置Agent"""
        self.steps = []
