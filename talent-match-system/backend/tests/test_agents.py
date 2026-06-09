import asyncio
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

class TestOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
    
    @patch('modules.agents.orchestrator.get_llm_client')
    @patch('modules.agents.orchestrator.TaskPlanner')
    @patch('modules.agents.orchestrator.ReActAgent')
    def test_orchestrator_initialization(self, mock_react, mock_planner, mock_llm):
        from modules.agents.orchestrator import OrchestratorAgent
        
        agent = OrchestratorAgent(user_id="test_user", session_id="test_session")
        
        self.assertEqual(agent.user_id, "test_user")
        self.assertEqual(agent.session_id, "test_session")
        self.assertIsNotNone(agent.tool_registry)
        self.assertIsNotNone(agent.memory_manager)
        self.assertEqual(len(agent.tool_registry.list_tools()), 10)
    
    @patch('modules.agents.orchestrator.get_llm_client')
    def test_explore_task(self, mock_llm):
        from modules.agents.orchestrator import OrchestratorAgent
        
        agent = OrchestratorAgent(user_id="test_user")
        
        result = self.loop.run_until_complete(
            agent.explore("resume_parse", {"resume_text": "test resume"})
        )
        
        self.assertEqual(result["task_type"], "resume_parse")
        self.assertIn("params", result)
        self.assertIn("timestamp", result)
        self.assertIn("session_id", result)
    
    def test_rule_based_planning(self):
        from modules.agents.orchestrator import OrchestratorAgent
        
        agent = OrchestratorAgent(user_id="test_user")
        
        plans = self.loop.run_until_complete(
            agent._rule_based_plan("resume_parse", {"resume_text": "test"})
        )
        
        self.assertIsInstance(plans, list)
        self.assertGreater(len(plans), 0)
        self.assertEqual(plans[0]["agent"], "resume_agent")
        self.assertEqual(plans[0]["action"], "parse_resume")
    
    def test_get_system_status(self):
        from modules.agents.orchestrator import OrchestratorAgent
        
        agent = OrchestratorAgent(user_id="test_user")
        
        status = self.loop.run_until_complete(agent.get_system_status())
        
        self.assertEqual(status["status"], "healthy")
        self.assertIn("agents", status)
        self.assertIn("tools", status)
        self.assertEqual(status["tools"]["registered_count"], 10)

class TestMatchAgent(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
    
    def test_calculate_match_basic(self):
        from modules.agents.match_agent import MatchAgent
        
        agent = MatchAgent()
        
        resume_profile = {
            "skills": ["Python", "Java", "MySQL"],
            "experience_years": "3年",
            "education": "本科",
            "location": "北京"
        }
        
        job_profile = {
            "required_skills": ["Python", "Java", "Vue"],
            "required_experience": "2年以上",
            "required_education": "本科及以上",
            "location": "北京"
        }
        
        result = agent.calculate_match(resume_profile, job_profile)
        
        self.assertIn("match_score", result)
        self.assertIn("skill_score", result)
        self.assertIn("match_strengths", result)
        self.assertIn("match_gaps", result)
        self.assertGreater(result["match_score"], 0)
        self.assertLess(result["match_score"], 100)
    
    def test_skill_gap_analysis(self):
        from modules.agents.match_agent import MatchAgent
        
        agent = MatchAgent()
        
        resume_skills = ["Python", "Java"]
        job_skills = ["Python", "Java", "Vue", "Docker"]
        
        result = agent.get_skill_gap_analysis(resume_skills, job_skills)
        
        self.assertEqual(result["total_required"], 4)
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["missing_count"], 2)
        self.assertIn("missing_skills", result)
        self.assertIn("skill_gap_details", result)
    
    def test_enhance_match(self):
        from modules.agents.match_agent import MatchAgent
        
        agent = MatchAgent()
        
        match_result = {
            "match_score": 75,
            "matched_skills": ["Python"],
            "missing_skills": ["Vue"]
        }
        
        resume_profile = {
            "skills": ["Python"],
            "experience_years": "3年"
        }
        
        job_profile = {
            "required_skills": ["Python", "Vue"],
            "job_responsibilities": ["负责前端开发"]
        }
        
        enhanced = agent.enhance_match(match_result, resume_profile, job_profile)
        
        self.assertIn("skill_gap_analysis", enhanced)
        self.assertIn("learning_roadmap", enhanced)
        self.assertIn("interview_preparation", enhanced)

class TestResumeParseAgent(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
    
    def test_parse_empty_resume(self):
        from modules.agents.resume_agent import ResumeParseAgent
        
        agent = ResumeParseAgent()
        
        result = agent.parse_resume("")
        
        self.assertEqual(result["name"], "未提供")
        self.assertEqual(result["source"], "empty")
        self.assertEqual(result["confidence"], 0)
    
    @patch('utils.qwen_client.get_qwen_client')
    def test_parse_resume_fallback(self, mock_client):
        from modules.agents.resume_agent import ResumeParseAgent
        
        agent = ResumeParseAgent()
        
        resume_text = """
        姓名：张三
        电话：13800138000
        邮箱：zhangsan@example.com
        学历：本科
        
        技能：Python, Java, MySQL
        工作经验：3年
        """
        
        result = agent.parse_resume(resume_text, use_reasoning=False)
        
        self.assertEqual(result["name"], "张三")
        self.assertIn("skills", result)
        self.assertIn("source", result)
    
    def test_validate_profile(self):
        from modules.agents.resume_agent import ResumeParseAgent
        
        agent = ResumeParseAgent()
        
        profile = {
            "name": "张三",
            "phone": "13800138000",
            "skills": ["Python", "Java"]
        }
        
        validation = agent.validate_profile(profile)
        
        self.assertIn("is_valid", validation)
        self.assertIn("errors", validation)
        self.assertIn("suggestions", validation)
    
    def test_enrich_profile(self):
        from modules.agents.resume_agent import ResumeParseAgent
        
        agent = ResumeParseAgent()
        
        profile = {
            "name": "张三",
            "skills": ["Python", "Java"]
        }
        
        enriched = agent.enrich_profile(profile)
        
        self.assertIn("skills_detail", enriched)
        self.assertIn("skill_summary", enriched)

class TestJobParseAgent(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
    
    def test_parse_empty_job(self):
        from modules.agents.job_agent import JobParseAgent
        
        agent = JobParseAgent()
        
        result = agent.parse_job("")
        
        self.assertEqual(result["job_title"], "未提供")
        self.assertEqual(result["source"], "empty")
        self.assertEqual(result["confidence"], 0)
    
    def test_skill_categorization(self):
        from modules.agents.job_agent import JobParseAgent
        
        agent = JobParseAgent()
        
        skills = ["Python", "JavaScript", "Vue", "MySQL", "Docker", "Git"]
        categories = agent._categorize_skills(skills)
        
        self.assertIn("编程语言", categories)
        self.assertIn("框架", categories)
        self.assertIn("数据库", categories)
        self.assertIn("工具", categories)
        
        self.assertIn("Python", categories["编程语言"])
        self.assertIn("Vue", categories["框架"])
        self.assertIn("MySQL", categories["数据库"])
    
    def test_align_tags_with_resume(self):
        from modules.agents.job_agent import JobParseAgent
        
        agent = JobParseAgent()
        
        job_profile = {
            "required_skills": ["Python", "JavaScript", "Vue"]
        }
        
        resume_profile = {
            "skills": ["Python", "JS"]
        }
        
        result = agent.align_tags_with_resume(job_profile, resume_profile)
        
        self.assertIn("aligned_skills", result)
        self.assertIn("match_summary", result)
        self.assertEqual(result["total_required"], 3)

class TestMessageAgent(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
    
    def test_detect_sensitive_content(self):
        from modules.agents.message_agent import MessageAgent
        
        agent = MessageAgent(user_id="test_user")
        
        normal_content = "您好，我想了解一下岗位要求"
        result = agent.detect_sensitive_content(normal_content)
        
        self.assertFalse(result["has_sensitive"])
        self.assertEqual(result["action"], "allow")
        
        sensitive_content = "请问这个岗位的工资是多少？"
        result = agent.detect_sensitive_content(sensitive_content)
        
        self.assertTrue(result["has_sensitive"])
        self.assertIn("工资", result["sensitive_words"])
    
    def test_extract_key_info(self):
        from modules.agents.message_agent import MessageAgent
        
        agent = MessageAgent(user_id="test_user")
        
        messages = [
            {"content": "您好，我熟练使用Python和Java进行开发"},
            {"content": "我有3年工作经验"},
            {"content": "请问薪资待遇如何？"}
        ]
        
        result = agent.extract_key_info(messages)
        
        self.assertIn("skills", result)
        self.assertIn("experience", result)
        self.assertTrue(result["salary_discussed"])
    
    def test_conversation_context(self):
        from modules.agents.message_agent import MessageAgent
        
        agent = MessageAgent(user_id="test_user")
        
        agent._initialize_conversation_context(
            conversation_id=1,
            job_seeker_id="user1",
            company_id="company1",
            job_id=100,
            resume_id=200
        )
        
        context = agent.get_conversation_context(1)
        
        self.assertIsNotNone(context)
        self.assertEqual(context["conversation_id"], 1)
        self.assertIn("messages", context)
        self.assertIn("key_info", context)
    
    def test_update_conversation_context(self):
        from modules.agents.message_agent import MessageAgent
        
        agent = MessageAgent(user_id="test_user")
        
        agent._initialize_conversation_context(
            conversation_id=1,
            job_seeker_id="user1",
            company_id="company1",
            job_id=100,
            resume_id=200
        )
        
        agent._update_conversation_context(1, "user1", "我会Python、Java和MySQL")
        
        context = agent.get_conversation_context(1)
        
        self.assertEqual(len(context["messages"]), 1)
        self.assertIn("Python", context["key_info"]["skills_discussed"])

class TestAgentFactory(unittest.TestCase):
    def test_factory_singleton(self):
        from modules.agents.factory import AgentFactory
        
        factory1 = AgentFactory()
        factory2 = AgentFactory()
        
        self.assertIs(factory1, factory2)
    
    def test_create_agents(self):
        from modules.agents.factory import AgentFactory
        
        factory = AgentFactory()
        
        orchestrator = factory.create_orchestrator(user_id="test_user")
        
        self.assertIsNotNone(orchestrator)
        self.assertEqual(orchestrator.user_id, "test_user")
    
    def test_agent_registration(self):
        from modules.agents.factory import AgentFactory
        
        factory = AgentFactory()
        factory.clear_all_agents()
        
        mock_agent = Mock()
        factory.register_agent("test_agent", mock_agent)
        
        retrieved = factory.get_agent("test_agent")
        
        self.assertIs(retrieved, mock_agent)
    
    def test_create_user_session(self):
        from modules.agents.factory import create_user_session
        
        session = create_user_session("user123")
        
        self.assertEqual(session["user_id"], "user123")
        self.assertIn("orchestrator", session)
        self.assertIn("resume_agent", session)
        self.assertIn("job_agent", session)
        self.assertIn("match_agent", session)
        self.assertIn("message_agent", session)

class TestToolRegistry(unittest.TestCase):
    def test_tool_registration(self):
        from modules.agents.tools.registry import ToolRegistry
        from modules.agents.tools.base import BaseTool
        
        registry = ToolRegistry()
        
        mock_tool = Mock(spec=BaseTool)
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        mock_tool.get_schema = Mock(return_value={})
        
        registry.register(mock_tool)
        
        tool_names = [tool["name"] for tool in registry.list_tools()]
        self.assertIn("test_tool", tool_names)
    
    def test_get_tool(self):
        from modules.agents.tools.registry import ToolRegistry
        from modules.agents.tools.base import BaseTool
        
        registry = ToolRegistry()
        
        mock_tool = Mock(spec=BaseTool)
        mock_tool.name = "test_tool"
        
        registry.register(mock_tool)
        
        retrieved = registry.get_tool("test_tool")
        
        self.assertIs(retrieved, mock_tool)

if __name__ == '__main__':
    unittest.main()
