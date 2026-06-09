from typing import Dict, Any, Optional, Type
from utils.qwen_client import get_qwen_client
from modules.agents.orchestrator import OrchestratorAgent
from modules.agents.resume_agent import ResumeParseAgent
from modules.agents.job_agent import JobParseAgent
from modules.agents.match_agent import MatchAgent
from modules.agents.graph_agent import GraphAgent
from modules.agents.knowledge_base_agent import KnowledgeBaseAgent

# 临时修复：使用qwen_client替代
def get_llm_client():
    return get_qwen_client()

class AgentFactory:
    _instance = None
    _agents: Dict[str, Any] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AgentFactory._initialized:
            self._agents = {}
            AgentFactory._initialized = True
    
    def register_agent(self, name: str, agent: Any):
        self._agents[name] = agent
    
    def get_agent(self, name: str) -> Optional[Any]:
        return self._agents.get(name)
    
    def get_all_agents(self) -> Dict[str, Any]:
        return self._agents.copy()
    
    def create_orchestrator(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> OrchestratorAgent:
        agent = OrchestratorAgent(user_id=user_id, session_id=session_id)
        self.register_agent("orchestrator", agent)
        return agent
    
    def create_resume_agent(self) -> ResumeParseAgent:
        if "resume_agent" not in self._agents:
            agent = ResumeParseAgent()
            self.register_agent("resume_agent", agent)
        return self._agents["resume_agent"]
    
    def create_job_agent(self) -> JobParseAgent:
        if "job_agent" not in self._agents:
            agent = JobParseAgent()
            self.register_agent("job_agent", agent)
        return self._agents["job_agent"]
    
    def create_match_agent(self) -> MatchAgent:
        if "match_agent" not in self._agents:
            agent = MatchAgent()
            self.register_agent("match_agent", agent)
        return self._agents["match_agent"]
    
    def create_graph_agent(self) -> GraphAgent:
        if "graph_agent" not in self._agents:
            agent = GraphAgent()
            self.register_agent("graph_agent", agent)
        return self._agents["graph_agent"]
    
    def create_knowledge_base_agent(self) -> KnowledgeBaseAgent:
        if "knowledge_base_agent" not in self._agents:
            agent = KnowledgeBaseAgent()
            self.register_agent("knowledge_base_agent", agent)
        return self._agents["knowledge_base_agent"]
    
    def create_all_agents(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        agents = {
            "resume_agent": self.create_resume_agent(),
            "job_agent": self.create_job_agent(),
            "match_agent": self.create_match_agent(),
            "graph_agent": self.create_graph_agent(),
            "knowledge_base_agent": self.create_knowledge_base_agent(),
            "orchestrator": self.create_orchestrator(user_id, session_id)
        }
        return agents
    
    def clear_all_agents(self):
        self._agents.clear()
    
    def remove_agent(self, name: str):
        if name in self._agents:
            del self._agents[name]

class AgentContainer:
    def __init__(self):
        self.factory = AgentFactory()
        self._singletons: Dict[str, Any] = {}
    
    def get_orchestrator(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> OrchestratorAgent:
        key = f"orchestrator_{user_id}_{session_id}" if user_id else "orchestrator_default"
        if key not in self._singletons:
            self._singletons[key] = self.factory.create_orchestrator(user_id, session_id)
        return self._singletons[key]
    
    def get_resume_agent(self) -> ResumeParseAgent:
        return self.factory.create_resume_agent()
    
    def get_job_agent(self) -> JobParseAgent:
        return self.factory.create_job_agent()
    
    def get_match_agent(self) -> MatchAgent:
        return self.factory.create_match_agent()
    
    def get_knowledge_base_agent(self) -> KnowledgeBaseAgent:
        return self.factory.create_knowledge_base_agent()
    
    def get_all_agents(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        return self.factory.create_all_agents(user_id, session_id)
    
    def inject_dependencies(self, agent: Any, dependencies: Dict[str, Any]):
        for dep_name, dep_instance in dependencies.items():
            if hasattr(agent, dep_name):
                setattr(agent, dep_name, dep_instance)
        return agent

def get_agent_factory() -> AgentFactory:
    return AgentFactory()

def get_agent_container() -> AgentContainer:
    return AgentContainer()

def get_default_orchestrator(user_id: Optional[str] = None, session_id: Optional[str] = None) -> OrchestratorAgent:
    container = get_agent_container()
    return container.get_orchestrator(user_id, session_id)

def create_user_session(user_id: str) -> Dict[str, Any]:
    container = get_agent_container()
    orchestrator = container.get_orchestrator(
        user_id=user_id,
        session_id=f"session_{user_id}"
    )
    
    return {
        "user_id": user_id,
        "orchestrator": orchestrator,
        "resume_agent": container.get_resume_agent(),
        "job_agent": container.get_job_agent(),
        "match_agent": container.get_match_agent(),
        "knowledge_base_agent": container.get_knowledge_base_agent()
    }
