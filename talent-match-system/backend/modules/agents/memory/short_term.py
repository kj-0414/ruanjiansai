"""
短期记忆模块
提供对话上下文缓冲功能
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class Message:
    """对话消息"""

    def __init__(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
        timestamp: Optional[str] = None
    ):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        return f"Message(role={self.role}, content={self.content[:50]}...)"


class ConversationBufferMemory:
    """
    对话缓冲记忆
    存储当前对话的完整上下文
    """

    def __init__(
        self,
        max_messages: int = 50,
        max_tokens: int = 4000,
        return_messages: bool = True
    ):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.return_messages = return_messages
        self.messages: List[Message] = []
        self.logger = logger

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """添加消息"""
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)

        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

        self.logger.debug(f"Added message: role={role}, total={len(self.messages)}")

    def get_messages(self) -> List[Message]:
        """获取所有消息"""
        return self.messages

    def get_conversation_string(self, separator: str = "\n") -> str:
        """获取对话字符串"""
        return separator.join(
            f"{msg.role}: {msg.content}" for msg in self.messages
        )

    def clear(self) -> None:
        """清空记忆"""
        self.messages.clear()
        self.logger.debug("Memory cleared")

    def get_recent_messages(self, n: int = 10) -> List[Message]:
        """获取最近的n条消息"""
        return self.messages[-n:] if n > 0 else self.messages

    def search_messages(
        self,
        keyword: str,
        case_sensitive: bool = False
    ) -> List[Message]:
        """搜索包含关键词的消息"""
        results = []
        keyword_lower = keyword if case_sensitive else keyword.lower()

        for msg in self.messages:
            content = msg.content if case_sensitive else msg.content.lower()
            if keyword_lower in content:
                results.append(msg)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        roles = {}
        for msg in self.messages:
            roles[msg.role] = roles.get(msg.role, 0) + 1

        return {
            "total_messages": len(self.messages),
            "roles": roles,
            "oldest_message": self.messages[0].timestamp if self.messages else None,
            "newest_message": self.messages[-1].timestamp if self.messages else None
        }


class ShortTermMemory:
    """
    短期记忆管理器
    为Agent提供当前任务相关的上下文
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.buffer = ConversationBufferMemory()
        self.context_stack: List[Dict] = []
        self.metadata: Dict[str, Any] = {}
        self.logger = logger

    def save_context(
        self,
        input_data: Any,
        output_data: Any,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        保存上下文

        Args:
            input_data: 输入数据
            output_data: 输出数据
            metadata: 元数据
        """
        context = {
            "input": self._serialize(input_data),
            "output": self._serialize(output_data),
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }

        self.context_stack.append(context)

        self.buffer.add_message(
            role="user",
            content=str(input_data),
            metadata={"type": "input"}
        )
        self.buffer.add_message(
            role="assistant",
            content=str(output_data),
            metadata={"type": "output"}
        )

    def _serialize(self, data: Any) -> str:
        """序列化数据"""
        if isinstance(data, str):
            return data
        try:
            return json.dumps(data, ensure_ascii=False)
        except:
            return str(data)

    def load_memory_variables(self) -> Dict[str, Any]:
        """
        加载记忆变量

        Returns:
            包含所有记忆变量的字典
        """
        return {
            "chat_history": self.buffer.get_messages() if self.buffer.return_messages
                            else self.buffer.get_conversation_string(),
            "recent_inputs": [
                ctx["input"] for ctx in self.context_stack[-5:]
            ],
            "recent_outputs": [
                ctx["output"] for ctx in self.context_stack[-5:]
            ],
            "session_id": self.session_id,
            "metadata": self.metadata
        }

    def clear(self) -> None:
        """清空所有记忆"""
        self.buffer.clear()
        self.context_stack.clear()
        self.metadata.clear()
        self.logger.info(f"Cleared all memory for session: {self.session_id}")

    def get_context_window(self, n: int = 10) -> List[Dict]:
        """获取最近n个上下文"""
        return self.context_stack[-n:]

    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
