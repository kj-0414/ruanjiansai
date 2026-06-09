import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from utils.qwen_client import get_qwen_client
from .resume_agent import ResumeParseAgent
from .job_agent import JobParseAgent
from .match_agent import MatchAgent
from .graph_agent import GraphAgent
from .knowledge_base_agent import KnowledgeBaseAgent
from .reasoning.planner import TaskPlanner
from .reasoning.react import ReActAgent
from .tools.registry import ToolRegistry
from .memory.manager import MemoryManager
from utils.prompt_templates import get_resume_prompt, get_job_prompt, get_match_prompt

logger = logging.getLogger(__name__)

# 临时修复：使用qwen_client替代
def get_llm_client():
    return get_qwen_client()

class OrchestratorAgent:
    def __init__(self, user_id: Optional[str] = None, session_id: Optional[str] = None):
        self.user_id = user_id or "default_user"
        self.session_id = session_id or f"session_{datetime.now().timestamp()}"
        
        self.resume_agent = ResumeParseAgent()
        self.job_agent = JobParseAgent()
        self.match_agent = MatchAgent()
        self.graph_agent = GraphAgent()
        self.knowledge_base_agent = KnowledgeBaseAgent()
        
        self.tool_registry = self._initialize_tool_registry()
        self.memory_manager = MemoryManager(self.user_id, self.session_id)
        self.task_planner = TaskPlanner(
            llm_client=get_llm_client()
        )
        self.react_agent = ReActAgent(
            llm_client=get_llm_client(),
            tool_executor=self.tool_registry
        )
        
        self.timeout_threshold = 3
        self.retry_count = 2
        self.retry_delay = 0.5
        self.max_plan_iterations = 5
        
        self.task_history: List[Dict[str, Any]] = []

    def _initialize_tool_registry(self) -> ToolRegistry:
        registry = ToolRegistry()
        
        from .tools.skill_tools import (
            normalize_skill_tool,
            get_related_skills_tool,
            get_skill_recommendations_tool,
            get_skill_trend_tool
        )
        from .tools.match_tools import (
            calculate_match_tool,
            enhance_match_tool,
            get_skill_gap_tool
        )
        from .tools.parse_tools import (
            parse_resume_tool,
            parse_job_tool,
            extract_skills_tool
        )
        
        registry.register(normalize_skill_tool)
        registry.register(get_related_skills_tool)
        registry.register(get_skill_recommendations_tool)
        registry.register(get_skill_trend_tool)
        registry.register(calculate_match_tool)
        registry.register(enhance_match_tool)
        registry.register(get_skill_gap_tool)
        registry.register(parse_resume_tool)
        registry.register(parse_job_tool)
        registry.register(extract_skills_tool)
        
        return registry

    async def explore(self, task_type: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.memory_manager.remember("system", f"Exploring task: {task_type}", {"task_type": task_type})
        
        exploration_context = context or {}
        if "conversation_history" not in exploration_context:
            conversation_history = self.memory_manager.recall(
                f"recent context about {task_type}",
                memory_type="short"
            )
            exploration_context["conversation_history"] = conversation_history
        
        similar_tasks = self._find_similar_tasks(task_type, params)
        if similar_tasks:
            exploration_context["similar_tasks"] = similar_tasks
        
        return {
            "task_type": task_type,
            "params": params,
            "context": exploration_context,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id
        }

    def _find_similar_tasks(self, task_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        similar = []
        for task in self.task_history[-10:]:
            if task.get("task_type") == task_type:
                similarity_score = self._calculate_task_similarity(params, task.get("params", {}))
                if similarity_score > 0.5:
                    similar.append({
                        "task": task,
                        "score": similarity_score
                    })
        return sorted(similar, key=lambda x: x["score"], reverse=True)[:3]

    def _calculate_task_similarity(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> float:
        common_keys = set(params1.keys()) & set(params2.keys())
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if params1[key] == params2[key]:
                matches += 1
        
        return matches / len(common_keys)

    async def plan(self, exploration_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_type = exploration_result["task_type"]
        params = exploration_result["params"]
        context = exploration_result.get("context", {})
        
        try:
            llm_plan = await self.task_planner.create_plan(
                task_description=f"{task_type} task with params: {json.dumps(params, ensure_ascii=False)}",
                available_tools=list(self.tool_registry.list_tools().keys()),
                context=context
            )
            
            if llm_plan and llm_plan.get("steps"):
                plans = self._convert_llm_plan_to_execution_plan(llm_plan, task_type, params)
                if plans:
                    self.memory_manager.remember(
                        "system",
                        f"LLM-generated plan for {task_type}",
                        {"plan": llm_plan, "task_type": task_type}
                    )
                    return plans
        except Exception as e:
            logger.warning(f"LLM planning failed: {e}, falling back to rule-based planning", exc_info=True)
        
        return await self._rule_based_plan(task_type, params, context)

    def _convert_llm_plan_to_execution_plan(self, llm_plan: Dict[str, Any], task_type: str, original_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        plans = []
        
        for step in llm_plan.get("steps", []):
            plan_item = {
                "agent": step.get("agent", step.get("tool_name", "").split("_")[0] + "_agent"),
                "action": step.get("action", step.get("tool_name")),
                "params": step.get("params", {}),
                "requires": step.get("requires", []),
                "provides": step.get("provides", []),
                "reasoning": step.get("reasoning", ""),
                "source": "llm"
            }
            
            for key, value in original_params.items():
                if key not in plan_item["params"]:
                    plan_item["params"][key] = value
            
            plans.append(plan_item)
        
        return plans

    async def _rule_based_plan(self, task_type: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if context is None:
            context = {}
        plans = []
        
        if task_type == "resume_parse":
            plans.extend(await self._plan_resume_parsing(params))
        
        elif task_type == "job_parse":
            plans.extend(await self._plan_job_parsing(params))
        
        elif task_type == "match":
            plans.extend(await self._plan_matching(params))
        
        
        
        elif task_type == "skill_analysis":
            plans.extend(await self._plan_skill_analysis(params))
        
        elif task_type == "knowledge_query":
            plans.extend(await self._plan_knowledge_query(params))
        
        elif task_type == "complex":
            plans.extend(await self._plan_complex_task(params))
        
        self.memory_manager.remember(
            "system",
            f"Rule-based plan created for {task_type}",
            {"plans": plans, "task_type": task_type}
        )
        
        return plans

    async def _plan_resume_parsing(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "agent": "resume_agent",
                "action": "parse_resume",
                "params": {"resume_text": params.get("resume_text", "")},
                "requires": [],
                "provides": ["resume_profile"]
            }
        ]

    async def _plan_job_parsing(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "agent": "job_agent",
                "action": "parse_job",
                "params": {"job_text": params.get("job_text", "")},
                "requires": [],
                "provides": ["job_profile"]
            }
        ]

    async def _plan_matching(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        plans = []
        
        if "resume_text" in params and not params.get("resume_profile"):
            plans.append({
                "agent": "resume_agent",
                "action": "parse_resume",
                "params": {"resume_text": params.get("resume_text", "")},
                "requires": [],
                "provides": ["resume_profile"]
            })
        
        if "job_text" in params and not params.get("job_profile"):
            plans.append({
                "agent": "job_agent",
                "action": "parse_job",
                "params": {"job_text": params.get("job_text", "")},
                "requires": [],
                "provides": ["job_profile"]
            })
        
        plans.append({
            "agent": "match_agent",
            "action": "calculate_match",
            "params": {
                "resume_profile": "{{resume_profile}}",
                "job_profile": "{{job_profile}}"
            },
            "requires": ["resume_profile", "job_profile"],
            "provides": ["match_result"]
        })
        
        plans.append({
            "agent": "match_agent",
            "action": "get_skill_gap_analysis",
            "params": {
                "resume_skills": "{{resume_profile}}.get('skills', [])",
                "job_skills": "{{job_profile}}.get('required_skills', [])"
            },
            "requires": ["resume_profile", "job_profile"],
            "provides": ["skill_gap_analysis"]
        })
        
        plans.append({
            "agent": "graph_agent",
            "action": "generate_graph",
            "params": {
                "match_result": "{{match_result}}"
            },
            "requires": ["match_result"],
            "provides": ["ability_graph"]
        })
        
        return plans

    async def _plan_skill_analysis(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "agent": "knowledge_base_agent",
                "action": "search_skills",
                "params": {
                    "query": params.get("query", ""),
                    "category": params.get("category")
                },
                "requires": [],
                "provides": ["skill_search_results"]
            },
            {
                "agent": "knowledge_base_agent",
                "action": "get_skill_relations",
                "params": {
                    "skill_id": params.get("skill_id")
                },
                "requires": ["skill_search_results"],
                "provides": ["skill_relations"]
            }
        ]

    async def _plan_knowledge_query(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "agent": "knowledge_base_agent",
                "action": "query_knowledge_base",
                "params": {
                    "query": params.get("query", ""),
                    "filters": params.get("filters", {})
                },
                "requires": [],
                "provides": ["knowledge_results"]
            }
        ]

    async def _plan_complex_task(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_description = params.get("description", "")
        
        try:
            react_result = await self.react_agent.think(
                question=task_description,
                context=json.dumps(params.get("context", {}), ensure_ascii=False)
            )
            
            plans = []
            for step in react_result.get("steps", []):
                if step.get("tool"):
                    tool_name = step["tool"]
                    plan_item = {
                        "agent": self._get_agent_for_tool(tool_name),
                        "action": tool_name,
                        "params": step.get("tool_input", {}),
                        "requires": [],
                        "provides": [tool_name.replace("_tool", "_result")],
                        "reasoning": step.get("thought", ""),
                        "source": "react"
                    }
                    plans.append(plan_item)
            
            return plans
        except Exception as e:
            logger.error(f"ReAct planning failed: {e}", exc_info=True)
            return []

    def _get_agent_for_tool(self, tool_name: str) -> str:
        tool_agent_mapping = {
            "normalize_skill": "knowledge_base_agent",
            "get_related_skills": "knowledge_base_agent",
            "get_skill_recommendations": "knowledge_base_agent",
            "calculate_match": "match_agent",
            "enhance_match": "match_agent",
            "get_skill_gap": "match_agent",
            "parse_resume": "resume_agent",
            "parse_job": "job_agent",
            "extract_skills": "resume_agent",
            "generate_graph": "graph_agent",
        }
        
        for prefix, agent in tool_agent_mapping.items():
            if tool_name.startswith(prefix):
                return agent
        
        return "knowledge_base_agent"

    async def act(self, plans: List[Dict[str, Any]], db=None) -> Dict[str, Any]:
        results = {}
        errors = []
        executed_order = []
        
        for iteration in range(self.max_plan_iterations):
            remaining_plans = [p for p in plans if p not in executed_order]
            
            if not remaining_plans:
                break
            
            executable_plans = self._get_executable_plans(remaining_plans, results)
            
            if not executable_plans:
                if remaining_plans:
                    errors.append({
                        "plan": remaining_plans[0],
                        "error": "Dependencies not satisfied"
                    })
                    executed_order.append(remaining_plans[0])
                continue
            
            for plan in executable_plans:
                try:
                    result = await self._execute_plan(plan, results, db)
                    for key in plan.get("provides", []):
                        results[key] = result
                    executed_order.append(plan)
                    
                    self.memory_manager.remember(
                        "system",
                        f"Executed {plan['action']} successfully",
                        {"result_summary": str(result)[:200], "plan": plan}
                    )
                except Exception as e:
                    errors.append({
                        "agent": plan["agent"],
                        "action": plan["action"],
                        "error": str(e),
                        "plan": plan
                    })
                    executed_order.append(plan)
        
        return {
            "success": len(errors) == 0,
            "results": results,
            "errors": errors,
            "executed_count": len(executed_order),
            "total_plans": len(plans)
        }

    def _get_executable_plans(self, plans: List[Dict[str, Any]], results: Dict[str, Any]) -> List[Dict[str, Any]]:
        executable = []
        
        for plan in plans:
            requires = plan.get("requires", [])
            
            can_execute = True
            for req in requires:
                if req not in results and req not in results.get("params", {}):
                    can_execute = False
                    break
            
            if can_execute:
                executable.append(plan)
        
        return executable

    async def _execute_plan(self, plan: Dict[str, Any], results: Dict[str, Any], db=None):
        agent_name = plan["agent"]
        action = plan["action"]
        params = self._resolve_params(plan["params"], results)
        
        tool_name = f"{action}_tool" if action in self.tool_registry.list_tools() else None
        
        if tool_name and tool_name in self.tool_registry.list_tools():
            return await self._execute_with_tool(tool_name, params, db)
        else:
            return await self._call_agent(agent_name, action, params, db)

    async def _execute_with_tool(self, tool_name: str, params: Dict[str, Any], db=None) -> Any:
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        try:
            if asyncio.iscoroutinefunction(tool.execute):
                result = await tool.execute(**params)
            else:
                result = tool.execute(**params)
            
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}, error: {e}", exc_info=True)
            raise

    def _resolve_params(self, params: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                var_name = value[2:-2].strip()
                
                if "." in var_name:
                    parts = var_name.split(".")
                    obj = results
                    for part in parts:
                        if isinstance(obj, dict):
                            obj = obj.get(part, {})
                        elif hasattr(obj, part):
                            obj = getattr(obj, part)
                        else:
                            obj = {}
                    resolved[key] = obj
                else:
                    resolved[key] = results.get(var_name, value)
            elif isinstance(value, str) and value.startswith("{{") and "}}." in value:
                template = value[2:-1]
                if "}}." in template:
                    var_name, path = template.split("}}.", 1)
                    obj = results.get(var_name.strip(), {})
                    for part in path.split("."):
                        if isinstance(obj, dict):
                            obj = obj.get(part, {})
                        elif hasattr(obj, part):
                            obj = getattr(obj, part)
                        else:
                            obj = {}
                    resolved[key] = obj
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved

    async def _call_agent(self, agent_name: str, action: str, params: Dict[str, Any], db=None):
        agent_map = {
            "resume_agent": self.resume_agent,
            "job_agent": self.job_agent,
            "match_agent": self.match_agent,
            "graph_agent": self.graph_agent,
            "knowledge_base_agent": self.knowledge_base_agent
        }
        
        agent = agent_map.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        method = getattr(agent, action, None)
        if not method:
            raise ValueError(f"Unknown action {action} for agent {agent_name}")
        
        if asyncio.iscoroutinefunction(method):
            if db:
                return await method(**params, db=db)
            return await method(**params)
        else:
            if db:
                return method(**params, db=db)
            return method(**params)

    async def execute_task(self, task_type: str, params: Dict[str, Any], db=None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        task_record = {
            "task_type": task_type,
            "params": params,
            "start_time": datetime.now().isoformat()
        }
        
        try:
            exploration = await self.explore(task_type, params, context)
            task_record["exploration"] = exploration
            
            plans = await self.plan(exploration)
            task_record["plans"] = plans
            
            result = await self.act(plans, db)
            task_record["result"] = result
            task_record["success"] = result["success"]
            
        except Exception as e:
            task_record["error"] = str(e)
            task_record["success"] = False
            task_record["result"] = {
                "success": False,
                "error": str(e)
            }
        
        task_record["end_time"] = datetime.now().isoformat()
        self.task_history.append(task_record)
        
        self.memory_manager.remember(
            "system",
            f"Completed task: {task_type}",
            {
                "success": task_record.get("success", False),
                "duration": task_record.get("end_time"),
                "plans_executed": len(task_record.get("plans", []))
            }
        )
        
        return task_record.get("result", {})

    async def get_system_status(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agents": {
                "orchestrator": "active",
                "resume_agent": "active",
                "job_agent": "active",
                "match_agent": "active",
                "graph_agent": "active",
                "knowledge_base_agent": "active"
            },
            "tools": {
                "registered_count": len(self.tool_registry.list_tools()),
                "tools": [tool["name"] for tool in self.tool_registry.list_tools()]
            },
            "memory": {
                "short_term_messages": len(self.memory_manager.short_term.buffer.messages),
                "medium_term_sessions": len(self.memory_manager.medium_term.session_memory.sessions) if hasattr(self.memory_manager.medium_term, 'session_memory') else 0,
                "long_term_profile_keys": len(self.memory_manager.long_term.profile_memory.skill_profile.skills) if hasattr(self.memory_manager.long_term, 'profile_memory') else 0
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_available_tools(self) -> List[str]:
        return list(self.tool_registry.list_tools().keys())

    def get_conversation_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.memory_manager.recall("recent conversation", memory_type="short")[:limit]

    async def reset_session(self):
        self.task_history.clear()
        self.memory_manager.short_term.clear()
        self.session_id = f"session_{datetime.now().timestamp()}"
        self.memory_manager.session_id = self.session_id
