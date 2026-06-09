from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging
from modules.agents.orchestrator import OrchestratorAgent
from modules.agents.resume_agent import ResumeParseAgent
from modules.agents.job_agent import JobParseAgent
from modules.agents.match_agent import MatchAgent
from modules.agents.graph_agent import GraphAgent
from modules.agents.ability_analysis_agent import AbilityAnalysisAgent
from modules.agents.talent_match_orchestrator import TalentMatchOrchestrator
from models import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["智能体"])

# 使用工厂模式或延迟加载来避免全局变量问题
_orchestrator = None
_resume_agent = None
_job_agent = None
_match_agent = None
_graph_agent = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator


def get_resume_agent():
    global _resume_agent
    if _resume_agent is None:
        _resume_agent = ResumeParseAgent()
    return _resume_agent


def get_job_agent():
    global _job_agent
    if _job_agent is None:
        _job_agent = JobParseAgent()
    return _job_agent


def get_match_agent():
    global _match_agent
    if _match_agent is None:
        _match_agent = MatchAgent()
    return _match_agent


def get_graph_agent():
    global _graph_agent
    if _graph_agent is None:
        _graph_agent = GraphAgent()
    return _graph_agent


@router.get("/status")
async def get_agents_status():
    orchestrator = get_orchestrator()
    return await orchestrator.get_system_status()


@router.post("/parse/resume")
async def parse_resume(resume_text: str):
    agent = get_resume_agent()
    result = agent.parse_resume(resume_text)
    return {"success": True, "data": result}


@router.post("/parse/job")
async def parse_job(job_text: str):
    agent = get_job_agent()
    result = agent.parse_job(job_text)
    return {"success": True, "data": result}


@router.post("/match")
async def match_profiles(resume_text: str, job_text: str):
    resume_agent = get_resume_agent()
    job_agent = get_job_agent()
    match_agent = get_match_agent()
    graph_agent = get_graph_agent()

    resume_profile = resume_agent.parse_resume(resume_text)
    job_profile = job_agent.parse_job(job_text)
    match_result = match_agent.calculate_match(resume_profile, job_profile)
    graph_result = graph_agent.generate_graph(match_result)

    return {
        "success": True,
        "resume_profile": resume_profile,
        "job_profile": job_profile,
        "match_result": match_result,
        "graph_result": graph_result
    }


@router.post("/execute")
async def execute_task(task_type: str, params: dict, db: Session = Depends(get_db)):
    orchestrator = get_orchestrator()
    result = await orchestrator.execute_task(task_type, params, db)
    return result


@router.post("/graph/generate")
async def generate_graph(match_result: dict):
    agent = get_graph_agent()
    result = agent.generate_graph(match_result)
    return {"success": True, "data": result}


@router.post("/graph/report")
async def generate_report(match_result: dict, resume_profile: dict, job_profile: dict):
    agent = get_graph_agent()
    result = agent.generate_report(match_result, resume_profile, job_profile)
    return {"success": True, "data": result}


@router.get("/architecture-info")
async def get_architecture_info():
    """获取当前架构信息"""
    return {
        "success": True,
        "current_architecture": "business_oriented",
        "architectures": {
            "business_oriented": {
                "name": "业务导向架构",
                "description": "符合业务流程的智能体系统：简历解析 -> 能力分析 -> 岗位匹配"
            },
            "legacy": {
                "name": "传统架构",
                "description": "使用 OrchestratorAgent 编排的原生多智能体系统"
            }
        }
    }


@router.post("/ability/analyze")
async def analyze_ability(
    resume_data: dict,
    user_id: str,
    resume_id: str = None
):
    """能力分析端点 - 生成能力树、雷达图、文本分析"""
    agent = AbilityAnalysisAgent()
    result = agent.analyze_ability(resume_data, user_id, resume_id)
    return {"success": True, "data": result}


@router.post("/workflow/full")
async def execute_full_workflow(
    file_path: str,
    job_ids: list = None,
    user_id: str = "default",
    db: Session = Depends(get_db)
):
    """完整业务流程端点 - 简历解析 + 能力分析 + 岗位匹配"""
    orchestrator = TalentMatchOrchestrator()
    result = orchestrator.execute_full_workflow(file_path, job_ids, user_id, db)
    return result


@router.get("/workflow/status")
async def get_workflow_status():
    """获取业务流程系统状态"""
    orchestrator = TalentMatchOrchestrator()
    return orchestrator.get_status()
