"""
任务规划器
基于LLM的智能任务规划和执行
"""

from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """任务"""
    task_id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    executor: Optional[Callable] = None
    result: Any = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "result": str(self.result) if self.result else None,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


@dataclass
class Plan:
    """执行计划"""
    plan_id: str
    goal: str
    tasks: List[Task]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at,
            "task_count": len(self.tasks),
            "pending_count": sum(1 for t in self.tasks if t.status == TaskStatus.PENDING),
            "completed_count": sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        }

    def get_next_tasks(self) -> List[Task]:
        """获取可执行的任务"""
        completed_ids = {
            t.task_id for t in self.tasks
            if t.status == TaskStatus.COMPLETED
        }

        next_tasks = []
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            if all(dep in completed_ids for dep in task.dependencies):
                next_tasks.append(task)

        return next_tasks

    def is_complete(self) -> bool:
        """计划是否完成"""
        return all(
            t.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]
            for t in self.tasks
        )


class TaskPlanner:
    """
    任务规划器
    根据目标自动规划任务序列
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.logger = logger
        self.available_tools: Dict[str, Dict] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        executor: Optional[Callable] = None
    ):
        """注册可用工具"""
        self.available_tools[name] = {
            "description": description,
            "parameters": parameters,
            "executor": executor
        }

    def _format_tools_for_llm(self) -> str:
        """格式化工具列表供LLM使用"""
        if not self.available_tools:
            return "No tools available."

        descriptions = []
        for name, tool in self.available_tools.items():
            desc = f"\n- {name}: {tool['description']}"
            if tool.get('parameters'):
                params = ", ".join(tool['parameters'].keys())
                desc += f" (parameters: {params})"
            descriptions.append(desc)

        return "\n".join(descriptions)

    async def create_plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Plan:
        """
        创建执行计划

        Args:
            goal: 目标
            context: 上下文

        Returns:
            Plan
        """
        import uuid

        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        self.logger.info(f"Creating plan for goal: {goal}")

        if self.llm_client:
            try:
                tasks = await self._generate_tasks_with_llm(goal, context)
            except Exception as e:
                self.logger.error(f"LLM planning failed: {e}")
                tasks = self._generate_fallback_tasks(goal, context)
        else:
            tasks = self._generate_fallback_tasks(goal, context)

        plan = Plan(
            plan_id=plan_id,
            goal=goal,
            tasks=tasks,
            context=context or {}
        )

        return plan

    async def _generate_tasks_with_llm(
        self,
        goal: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Task]:
        """使用LLM生成任务"""
        prompt = f"""You are a HR assistant task planner.

Goal: {goal}

Available tools:
{self._format_tools_for_llm()}

Context:
{context}

Generate a task plan to achieve this goal. Respond in JSON format:
{{
  "tasks": [
    {{
      "task_id": "task_1",
      "name": "task name",
      "description": "what to do",
      "dependencies": []
    }}
  ]
}}

Consider:
1. Logical task ordering
2. Dependencies between tasks
3. Using appropriate tools for each task

Respond only with valid JSON."""

        try:
            response = await self._call_llm(prompt)
            import json
            data = json.loads(response)

            tasks = []
            for task_data in data.get("tasks", []):
                task = Task(
                    task_id=task_data.get("task_id", f"task_{len(tasks)}"),
                    name=task_data.get("name", ""),
                    description=task_data.get("description", ""),
                    dependencies=task_data.get("dependencies", [])
                )

                tool_name = task_data.get("tool")
                if tool_name and tool_name in self.available_tools:
                    task.executor = self.available_tools[tool_name].get("executor")

                tasks.append(task)

            return tasks

        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            return self._generate_fallback_tasks(goal, context)

    def _generate_fallback_tasks(
        self,
        goal: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Task]:
        """生成备用任务（基于关键词匹配）"""
        goal_lower = goal.lower()
        tasks = []

        if "match" in goal_lower or "匹配" in goal_lower:
            tasks.append(Task(
                task_id="task_parse_resume",
                name="Parse Resume",
                description="Extract information from resume",
                dependencies=[]
            ))
            tasks.append(Task(
                task_id="task_parse_job",
                name="Parse Job",
                description="Extract requirements from job posting",
                dependencies=[]
            ))
            tasks.append(Task(
                task_id="task_calculate_match",
                name="Calculate Match",
                description="Calculate match score between resume and job",
                dependencies=["task_parse_resume", "task_parse_job"]
            ))
            tasks.append(Task(
                task_id="task_generate_suggestions",
                name="Generate Suggestions",
                description="Generate improvement suggestions",
                dependencies=["task_calculate_match"]
            ))

        elif "skill" in goal_lower or "技能" in goal_lower:
            tasks.append(Task(
                task_id="task_normalize_skill",
                name="Normalize Skill",
                description="Normalize skill name",
                dependencies=[]
            ))
            tasks.append(Task(
                task_id="task_find_related",
                name="Find Related Skills",
                description="Find related skills",
                dependencies=["task_normalize_skill"]
            ))

        else:
            tasks.append(Task(
                task_id="task_analyze",
                name="Analyze Request",
                description="Analyze user request",
                dependencies=[]
            ))
            tasks.append(Task(
                task_id="task_execute",
                name="Execute Action",
                description="Execute the main action",
                dependencies=["task_analyze"]
            ))

        return tasks

    async def execute_plan(
        self,
        plan: Plan,
        context: Optional[Dict[str, Any]] = None
    ) -> Plan:
        """
        执行计划

        Args:
            plan: 计划
            context: 执行上下文

        Returns:
            完成的计划
        """
        self.logger.info(f"Executing plan: {plan.plan_id}")

        execution_context = context or {}
        max_iterations = len(plan.tasks) * 2

        for iteration in range(max_iterations):
            if plan.is_complete():
                break

            next_tasks = plan.get_next_tasks()

            if not next_tasks:
                if not plan.is_complete():
                    self.logger.warning("No tasks can be executed, possible dependency issue")
                break

            for task in next_tasks:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now().isoformat()

                try:
                    if task.executor:
                        result = task.executor(context=execution_context)
                        if hasattr(result, '__await__'):
                            result = await result
                        task.result = result
                    else:
                        task.result = f"Task {task.name} completed"

                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now().isoformat()

                    execution_context[task.task_id] = task.result

                except Exception as e:
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                    self.logger.error(f"Task {task.task_id} failed: {e}")

        self.logger.info(f"Plan execution completed: {plan.plan_id}")

        return plan

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        if self.llm_client:
            response = self.llm_client.chat(prompt)
            return response if isinstance(response, str) else str(response)
        return "{}"

    def get_execution_summary(self, plan: Plan) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "total_tasks": len(plan.tasks),
            "completed": sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED),
            "pending": sum(1 for t in plan.tasks if t.status == TaskStatus.PENDING),
            "results": {
                t.task_id: str(t.result) if t.result else None
                for t in plan.tasks if t.status == TaskStatus.COMPLETED
            }
        }
