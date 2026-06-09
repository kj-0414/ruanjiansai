"""
记忆管理器
统一管理短期、中期、长期记忆
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
import logging

from .short_term import ShortTermMemory
from .medium_term import MediumTermMemory
from .long_term import LongTermMemory

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    统一记忆管理器
    整合三层记忆系统，为Agent提供完整的记忆能力
    """

    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or f"session_{datetime.now().timestamp()}"

        self.short_term = ShortTermMemory(self.session_id)
        self.medium_term = MediumTermMemory(user_id)
        self.long_term = LongTermMemory(user_id)

        self.logger = logger

    def remember(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        存储记忆（同时存入三层记忆）

        Args:
            role: 角色 (user/assistant/system)
            content: 内容
            metadata: 元数据
        """
        self.short_term.buffer.add_message(role, content, metadata)

        self.medium_term.add_interaction(role, content, metadata)

        self.short_term.save_context(
            input_data={"role": role, "content": content},
            output_data={"status": "remembered"},
            metadata=metadata
        )

        self.logger.debug(f"Remembered: role={role}, content_length={len(content)}")

    def recall(
        self,
        query: str,
        memory_type: Optional[str] = None
    ) -> List[Dict]:
        """
        回忆（查询记忆）

        Args:
            query: 查询关键词
            memory_type: 记忆类型 (short/medium/long/all)

        Returns:
            匹配的记忆列表
        """
        results = []

        if memory_type in [None, "all", "short"]:
            short_results = self.short_term.buffer.search_messages(query)
            results.extend([
                {"type": "short_term", "data": msg.to_dict()}
                for msg in short_results
            ])

        if memory_type in [None, "all", "medium"]:
            medium_results = self.medium_term.session_memory.search_in_sessions(query)
            results.extend([
                {"type": "medium_term", "data": result}
                for result in medium_results
            ])

        if memory_type in [None, "all", "long"]:
            long_results = self.long_term.search_memory(query)
            results.extend([
                {"type": "long_term", "data": result}
                for result in long_results
            ])

        self.logger.debug(f"Recalled {len(results)} memories for query: {query}")
        return results

    def get_context(self) -> Dict[str, Any]:
        """
        获取完整上下文

        Returns:
            包含三层记忆的上下文字典
        """
        return {
            "short_term": self.short_term.load_memory_variables(),
            "medium_term": {
                "recent_interactions": self.medium_term.get_recent_interactions(10),
                "session_summary": self.medium_term.get_session_summary(self.session_id)
            },
            "long_term": self.long_term.get_summary()
        }

    def get_prompt_context(self, max_messages: int = 10) -> str:
        """
        获取用于LLM Prompt的上下文字符串

        Args:
            max_messages: 最大消息数

        Returns:
            格式化的上下文字符串
        """
        parts = []

        short_term = self.short_term.buffer.get_recent_messages(max_messages)
        if short_term:
            parts.append("Recent conversation:")
            for msg in short_term:
                parts.append(f"- {msg.role}: {msg.content}")

        long_term_summary = self.long_term.get_summary()
        if long_term_summary.get("total_skills", 0) > 0:
            top_skills = long_term_summary.get("top_skills", [])
            if top_skills:
                skills_str = ", ".join([s["skill"] for s in top_skills[:5]])
                parts.append(f"User's top skills: {skills_str}")

        return "\n".join(parts) if parts else "No relevant context available."

    def learn(
        self,
        skill_name: str,
        proficiency: int = 3,
        source: str = "interaction"
    ):
        """
        学习新技能（存入长期记忆）

        Args:
            skill_name: 技能名称
            proficiency: 熟练度
            source: 来源
        """
        self.long_term.profile_memory.skill_profile.add_skill(
            skill_name,
            proficiency,
            source
        )
        self.long_term.profile_memory._save_to_disk()

        self.logger.info(f"Learned skill: {skill_name} (proficiency: {proficiency})")

    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term.clear()
        self.logger.info("Short-term memory cleared")

    def clear_medium_term(self):
        """清空中期记忆"""
        if self.medium_term.session_memory.active_session_id:
            session_id = self.medium_term.session_memory.active_session_id
            self.medium_term.session_memory.delete_session(session_id)
        self.logger.info("Medium-term memory cleared")

    def clear_all(self):
        """清空所有记忆"""
        self.clear_short_term()
        self.clear_medium_term()
        self.logger.info("All memory cleared")

    def new_session(self, session_title: str = ""):
        """开始新会话"""
        self.short_term.clear()

        new_session_id = self.medium_term.new_interaction(session_title)
        self.session_id = new_session_id

        self.logger.info(f"Started new session: {new_session_id}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取记忆统计"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "short_term": {
                "message_count": len(self.short_term.buffer.messages),
                "context_count": len(self.short_term.context_stack)
            },
            "medium_term": self.medium_term.get_statistics(),
            "long_term": {
                "skill_count": len(self.long_term.profile_memory.skill_profile.skills),
                "interaction_count": len(self.long_term.profile_memory.interaction_history),
                "achievement_count": len(self.long_term.profile_memory.achievements)
            }
        }


_global_memory_managers: Dict[str, MemoryManager] = {}


def get_memory_manager(user_id: str, session_id: Optional[str] = None) -> MemoryManager:
    """
    获取全局记忆管理器

    Args:
        user_id: 用户ID
        session_id: 会话ID

    Returns:
        MemoryManager实例
    """
    key = f"{user_id}_{session_id}" if session_id else user_id

    if key not in _global_memory_managers:
        _global_memory_managers[key] = MemoryManager(user_id, session_id)

    return _global_memory_managers[key]
