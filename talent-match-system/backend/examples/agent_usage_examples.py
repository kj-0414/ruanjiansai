"""
人才匹配系统 - Agent架构使用示例

本文档展示如何使用增强后的Agent系统进行任务执行。
"""

import asyncio
from modules.agents import (
    get_default_orchestrator,
    create_user_session,
    AgentFactory,
    AgentContainer
)

async def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("基础使用示例")
    print("=" * 60)
    
    orchestrator = get_default_orchestrator(user_id="user001")
    
    status = await orchestrator.get_system_status()
    print(f"\n系统状态:")
    print(f"  - 已注册工具数: {status['tools']['registered_count']}")
    print(f"  - 可用工具: {', '.join(status['tools']['tools'][:5])}...")
    
    tools = orchestrator.get_available_tools()
    print(f"\n所有可用工具:")
    for tool in tools:
        print(f"  - {tool}")

async def example_resume_parsing():
    """简历解析示例"""
    print("\n" + "=" * 60)
    print("简历解析示例")
    print("=" * 60)
    
    orchestrator = get_default_orchestrator(user_id="user001")
    
    resume_text = """
    姓名：张三
    电话：13800138000
    邮箱：zhangsan@example.com
    学历：本科（计算机科学专业）
    
    工作经历：
    - 2020年至今：高级Python开发工程师
    - 2018-2020年：Java开发工程师
    
    技能：
    - 编程语言：Python, Java, JavaScript, Go
    - 框架：Vue.js, React, Django, Spring Boot
    - 数据库：MySQL, PostgreSQL, MongoDB, Redis
    - 工具：Git, Docker, Kubernetes, Jenkins
    - 其他：Linux, Nginx, AWS
    
    项目经验：
    - 电商平台后端开发（Python + Django）
    - 微服务架构设计与实现（Go + gRPC）
    - 前端架构升级（Vue.js + TypeScript）
    """
    
    result = await orchestrator.execute_task(
        task_type="resume_parse",
        params={"resume_text": resume_text}
    )
    
    print(f"\n解析结果:")
    if result.get("success"):
        results = result.get("results", {})
        if "resume_profile" in results:
            profile = results["resume_profile"]
            print(f"  - 姓名: {profile.get('name')}")
            print(f"  - 教育: {profile.get('education')}")
            print(f"  - 经验: {profile.get('experience_years')}")
            print(f"  - 技能数: {len(profile.get('skills', []))}")
            print(f"  - 技能分类: {profile.get('skill_categories', {})}")
    else:
        print(f"  - 错误: {result.get('errors')}")

async def example_job_parsing():
    """岗位解析示例"""
    print("\n" + "=" * 60)
    print("岗位解析示例")
    print("=" * 60)
    
    orchestrator = get_default_orchestrator(user_id="user001")
    
    job_text = """
    岗位名称：全栈开发工程师
    
    岗位描述：
    我们正在寻找一位全栈开发工程师，加入我们的产品团队，负责公司核心产品的开发和维护。
    
    技能要求：
    - 熟练掌握Python或Java
    - 熟悉前端框架（Vue.js或React）
    - 熟悉关系型数据库（MySQL/PostgreSQL）
    - 有微服务开发经验优先
    - 熟悉Docker和Kubernetes
    
    经验要求：3年以上开发经验
    
    学历要求：本科及以上
    
    薪资范围：20K-35K
    
    工作地点：北京
    """
    
    result = await orchestrator.execute_task(
        task_type="job_parse",
        params={"job_text": job_text}
    )
    
    print(f"\n解析结果:")
    if result.get("success"):
        results = result.get("results", {})
        if "job_profile" in results:
            profile = results["job_profile"]
            print(f"  - 岗位: {profile.get('job_title')}")
            print(f"  - 薪资: {profile.get('salary_range')}")
            print(f"  - 地点: {profile.get('location')}")
            print(f"  - 经验: {profile.get('required_experience')}")
            print(f"  - 学历: {profile.get('required_education')}")
            print(f"  - 技能数: {len(profile.get('required_skills', []))}")
            print(f"  - 技能难度: {profile.get('skill_difficulty_level')}")
    else:
        print(f"  - 错误: {result.get('errors')}")

async def example_matching():
    """人岗匹配示例"""
    print("\n" + "=" * 60)
    print("人岗匹配示例")
    print("=" * 60)
    
    orchestrator = get_default_orchestrator(user_id="user001")
    
    resume_text = """
    姓名：李四
    学历：本科
    工作经验：4年
    
    技能：Python, Java, Vue.js, MySQL, Docker, Redis
    """
    
    job_text = """
    岗位：全栈开发工程师
    要求：Python, Java, Vue.js, MySQL, PostgreSQL, Docker, Kubernetes
    经验：3年以上
    """
    
    result = await orchestrator.execute_task(
        task_type="match",
        params={
            "resume_text": resume_text,
            "job_text": job_text
        }
    )
    
    print(f"\n匹配结果:")
    if result.get("success"):
        results = result.get("results", {})
        if "match_result" in results:
            match = results["match_result"]
            print(f"  - 匹配分数: {match.get('match_score')}")
            print(f"  - 技能分数: {match.get('skill_score')}")
            print(f"  - 优势: {', '.join(match.get('match_strengths', [])[:2])}")
            print(f"  - 差距: {', '.join(match.get('match_gaps', [])[:2])}")
            print(f"  - 建议: {match.get('suggestions', [])[:1]}")
            
        if "skill_gap_analysis" in results:
            gap = results["skill_gap_analysis"]
            print(f"\n  技能差距分析:")
            print(f"    - 匹配率: {gap.get('match_rate')}%")
            print(f"    - 缺少技能: {gap.get('missing_skills', [])}")
            print(f"    - 学习优先级: {gap.get('learning_priority', [])}")
    else:
        print(f"  - 错误: {result.get('errors')}")

async def example_user_session():
    """完整用户会话示例"""
    print("\n" + "=" * 60)
    print("完整用户会话示例")
    print("=" * 60)
    
    session = create_user_session("user001")
    
    print(f"\n用户会话已创建:")
    print(f"  - 用户ID: {session['user_id']}")
    print(f"  - Orchestrator: {type(session['orchestrator']).__name__}")
    print(f"  - ResumeAgent: {type(session['resume_agent']).__name__}")
    print(f"  - MatchAgent: {type(session['match_agent']).__name__}")
    print(f"  - MessageAgent: {type(session['message_agent']).__name__}")
    
    status = await session['orchestrator'].get_system_status()
    print(f"\n系统状态:")
    print(f"  - 状态: {status['status']}")
    print(f"  - 工具数: {status['tools']['registered_count']}")
    print(f"  - 记忆消息数: {status['memory']['short_term_messages']}")

async def example_agent_factory():
    """Agent工厂示例"""
    print("\n" + "=" * 60)
    print("Agent工厂示例")
    print("=" * 60)
    
    factory = AgentFactory()
    
    print(f"\n创建Agent实例:")
    
    resume_agent = factory.create_resume_agent()
    print(f"  - ResumeParseAgent: ✓ (已注册)")
    
    job_agent = factory.create_job_agent()
    print(f"  - JobParseAgent: ✓ (已注册)")
    
    match_agent = factory.create_match_agent()
    print(f"  - MatchAgent: ✓ (已注册)")
    
    message_agent = factory.create_message_agent("user001")
    print(f"  - MessageAgent: ✓ (已注册)")
    
    print(f"\n获取已注册的Agent:")
    all_agents = factory.get_all_agents()
    print(f"  - 总数: {len(all_agents)}")
    for name in all_agents.keys():
        print(f"    • {name}")

async def example_memory_usage():
    """记忆系统使用示例"""
    print("\n" + "=" * 60)
    print("记忆系统使用示例")
    print("=" * 60)
    
    orchestrator = get_default_orchestrator(user_id="user001")
    
    print(f"\n记忆状态:")
    status = await orchestrator.get_system_status()
    print(f"  - 短期记忆消息数: {status['memory']['short_term_messages']}")
    print(f"  - 中期记忆会话数: {status['memory']['medium_term_sessions']}")
    
    print(f"\n上下文历史:")
    context = orchestrator.get_conversation_context(limit=5)
    print(f"  - 最近上下文数: {len(context)}")

async def example_skill_analysis():
    """技能分析示例"""
    print("\n" + "=" * 60)
    print("技能分析示例")
    print("=" * 60)
    
    orchestrator = get_default_orchestrator(user_id="user001")
    
    result = await orchestrator.execute_task(
        task_type="skill_analysis",
        params={
            "query": "Python",
            "category": "编程语言"
        }
    )
    
    print(f"\n技能分析结果:")
    if result.get("success"):
        results = result.get("results", {})
        if "skill_search_results" in results:
            skills = results["skill_search_results"]
            print(f"  - 找到相关技能: {len(skills)} 个")
            for skill in skills[:3]:
                print(f"    • {skill}")
    else:
        print(f"  - 错误: {result.get('errors')}")

async def example_complex_task():
    """复杂任务示例"""
    print("\n" + "=" * 60)
    print("复杂任务示例")
    print("=" * 60)
    
    orchestrator = get_default_orchestrator(user_id="user001")
    
    result = await orchestrator.execute_task(
        task_type="complex",
        params={
            "description": "分析候选人张三的简历，找出他与全栈工程师岗位的匹配度，并给出技能提升建议"
        }
    )
    
    print(f"\n复杂任务结果:")
    print(f"  - 成功: {result.get('success')}")
    print(f"  - 执行计划数: {result.get('executed_count', 0)}")
    print(f"  - 总计划数: {result.get('total_plans', 0)}")

async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("人才匹配系统 - Agent架构使用示例")
    print("=" * 60)
    
    try:
        await example_basic_usage()
        await example_resume_parsing()
        await example_job_parsing()
        await example_matching()
        await example_user_session()
        await example_agent_factory()
        await example_memory_usage()
        await example_skill_analysis()
        await example_complex_task()
        
        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
