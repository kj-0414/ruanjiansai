"""
中期记忆模块
提供会话历史和用户会话管理功能
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class Session:
    """会话数据"""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        title: str = "",
        summary: str = ""
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.title = title
        self.summary = summary
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.messages: List[Dict] = []
        self.context: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加消息"""
        self.messages.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": self.title,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": len(self.messages)
        }


class SessionMemory:
    """
    会话记忆
    管理用户的多个会话历史
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.sessions: Dict[str, Session] = {}
        self.active_session_id: Optional[str] = None
        self.logger = logger

    def create_session(self, session_id: str, title: str = "") -> Session:
        """创建新会话"""
        session = Session(
            session_id=session_id,
            user_id=self.user_id,
            title=title
        )
        self.sessions[session_id] = session
        self.active_session_id = session_id
        self.logger.info(f"Created session: {session_id} for user: {self.user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)

    def set_active_session(self, session_id: str) -> bool:
        """设置活跃会话"""
        if session_id in self.sessions:
            self.active_session_id = session_id
            return True
        return False

    def get_active_session(self) -> Optional[Session]:
        """获取活跃会话"""
        if self.active_session_id:
            return self.sessions.get(self.active_session_id)
        return None

    def add_message_to_active(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """向活跃会话添加消息"""
        session = self.get_active_session()
        if session:
            session.add_message(role, content, metadata)
            return True
        return False

    def list_sessions(
        self,
        limit: int = 10,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """列出用户的会话"""
        sessions = list(self.sessions.values())

        if since:
            sessions = [
                s for s in sessions
                if s.created_at >= since
            ]

        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        return [s.to_dict() for s in sessions[:limit]]

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.active_session_id == session_id:
                self.active_session_id = None
            self.logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def search_in_sessions(
        self,
        keyword: str,
        session_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """在会话中搜索"""
        results = []
        keyword_lower = keyword.lower()

        search_sessions = (
            [self.sessions[sid] for sid in session_ids if sid in self.sessions]
            if session_ids
            else self.sessions.values()
        )

        for session in search_sessions:
            for msg in session.messages:
                if keyword_lower in msg["content"].lower():
                    results.append({
                        "session_id": session.session_id,
                        "message": msg
                    })

        return results


class MediumTermMemory:
    """
    中期记忆管理器
    管理会话历史和跨会话上下文
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_memory = SessionMemory(user_id)
        self.cross_session_context: Dict[str, Any] = {}
        self.logger = logger

    def new_interaction(self, session_title: str = "") -> str:
        """开始新交互"""
        import uuid
        session_id = f"{self.user_id}_{uuid.uuid4().hex[:8]}"
        self.session_memory.create_session(session_id, session_title)
        return session_id

    def add_interaction(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """添加交互记录"""
        return self.session_memory.add_message_to_active(role, content, metadata)

    def get_recent_interactions(self, limit: int = 20) -> List[Dict]:
        """获取最近的交互"""
        session = self.session_memory.get_active_session()
        if session:
            return session.messages[-limit:]
        return []

    def get_session_summary(self, session_id: str) -> Optional[str]:
        """获取会话摘要"""
        session = self.session_memory.get_session(session_id)
        return session.summary if session else None

    def update_cross_context(self, key: str, value: Any) -> None:
        """更新跨会话上下文"""
        self.cross_session_context[key] = value
        self.logger.debug(f"Updated cross-session context: {key}")

    def get_cross_context(self, key: str, default: Any = None) -> Any:
        """获取跨会话上下文"""
        return self.cross_session_context.get(key, default)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "user_id": self.user_id,
            "total_sessions": len(self.session_memory.sessions),
            "active_session": self.session_memory.active_session_id,
            "cross_context_keys": list(self.cross_session_context.keys())
        }
