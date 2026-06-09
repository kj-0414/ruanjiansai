"""
长期记忆模块
提供用户画像和持久化记忆功能
"""

from typing import List, Dict, Optional, Any, Set
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class UserSkillProfile:
    """用户技能画像"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.preferred_categories: List[str] = []
        self.learning_history: List[Dict] = []
        self.updated_at = datetime.now()

    def add_skill(
        self,
        skill_name: str,
        proficiency: int = 3,
        source: str = "resume",
        metadata: Optional[Dict] = None
    ):
        """添加技能"""
        self.skills[skill_name] = {
            "proficiency": proficiency,
            "source": source,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat()
        }
        self.updated_at = datetime.now()

    def update_skill_proficiency(self, skill_name: str, proficiency: int):
        """更新技能熟练度"""
        if skill_name in self.skills:
            self.skills[skill_name]["proficiency"] = proficiency
            self.updated_at = datetime.now()

    def remove_skill(self, skill_name: str) -> bool:
        """移除技能"""
        if skill_name in self.skills:
            del self.skills[skill_name]
            self.updated_at = datetime.now()
            return True
        return False

    def get_skills_by_category(self, category: str) -> List[str]:
        """按分类获取技能"""
        return [
            name for name, info in self.skills.items()
            if info.get("metadata", {}).get("category") == category
        ]

    def get_top_skills(self, n: int = 10) -> List[Dict]:
        """获取最熟练的技能"""
        sorted_skills = sorted(
            self.skills.items(),
            key=lambda x: x[1].get("proficiency", 0),
            reverse=True
        )
        return [
            {"skill": name, **info}
            for name, info in sorted_skills[:n]
        ]

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "skills": self.skills,
            "preferred_categories": self.preferred_categories,
            "learning_history": self.learning_history,
            "updated_at": self.updated_at.isoformat()
        }


class UserProfileMemory:
    """
    用户画像记忆
    存储用户的长期偏好、技能和历史
    """

    def __init__(self, user_id: str, storage_path: Optional[str] = None):
        self.user_id = user_id
        self.storage_path = storage_path or self._get_default_path()

        self.skill_profile = UserSkillProfile(user_id)
        self.preferences: Dict[str, Any] = {}
        self.interaction_history: List[Dict] = []
        self.achievements: Set[str] = set()
        self.notes: Dict[str, str] = {}

        self._load_from_disk()

    def _get_default_path(self) -> str:
        """获取默认存储路径"""
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return str(data_dir / f"user_profile_{self.user_id}.json")

    def _load_from_disk(self):
        """从磁盘加载"""
        try:
            path = Path(self.storage_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.preferences = data.get("preferences", {})
                self.interaction_history = data.get("interaction_history", [])
                self.achievements = set(data.get("achievements", []))

                if "skill_profile" in data:
                    sp_data = data["skill_profile"]
                    self.skill_profile = UserSkillProfile(self.user_id)
                    self.skill_profile.skills = sp_data.get("skills", {})
                    self.skill_profile.preferred_categories = sp_data.get("preferred_categories", [])

                logger.info(f"Loaded profile for user: {self.user_id}")

        except Exception as e:
            logger.warning(f"Failed to load profile: {e}")

    def _save_to_disk(self):
        """保存到磁盘"""
        try:
            path = Path(self.storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "user_id": self.user_id,
                "preferences": self.preferences,
                "interaction_history": self.interaction_history[-100:],
                "achievements": list(self.achievements),
                "skill_profile": self.skill_profile.to_dict(),
                "updated_at": datetime.now().isoformat()
            }

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved profile for user: {self.user_id}")

        except Exception as e:
            logger.error(f"Failed to save profile: {e}")

    def update_preference(self, key: str, value: Any):
        """更新偏好"""
        self.preferences[key] = value
        self._save_to_disk()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取偏好"""
        return self.preferences.get(key, default)

    def add_interaction(self, interaction_type: str, content: Any, metadata: Optional[Dict] = None):
        """添加交互记录"""
        self.interaction_history.append({
            "type": interaction_type,
            "content": str(content),
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })

        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-1000:]

        self._save_to_disk()

    def get_interaction_stats(self) -> Dict[str, Any]:
        """获取交互统计"""
        types = {}
        for interaction in self.interaction_history:
            t = interaction["type"]
            types[t] = types.get(t, 0) + 1

        return {
            "total_interactions": len(self.interaction_history),
            "interaction_types": types,
            "latest_interaction": self.interaction_history[-1] if self.interaction_history else None
        }

    def add_achievement(self, achievement: str):
        """添加成就"""
        self.achievements.add(achievement)
        self._save_to_disk()

    def has_achievement(self, achievement: str) -> bool:
        """检查成就"""
        return achievement in self.achievements

    def get_all_data(self) -> Dict[str, Any]:
        """获取所有数据"""
        return {
            "user_id": self.user_id,
            "skill_profile": self.skill_profile.to_dict(),
            "preferences": self.preferences,
            "interaction_stats": self.get_interaction_stats(),
            "achievements": list(self.achievements),
            "notes": self.notes
        }


class LongTermMemory:
    """
    长期记忆管理器
    整合用户画像和持久化记忆
    """

    def __init__(self, user_id: str, storage_path: Optional[str] = None):
        self.user_id = user_id
        self.profile_memory = UserProfileMemory(user_id, storage_path)
        self.logger = logger

    def get_user_skills(self) -> Dict[str, Dict[str, Any]]:
        """获取用户技能"""
        return self.profile_memory.skill_profile.skills

    def update_user_skills(self, skills: List[str], source: str = "interaction"):
        """更新用户技能"""
        for skill in skills:
            self.profile_memory.skill_profile.add_skill(skill, source=source)

    def get_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        return self.profile_memory.preferences

    def learn_from_interaction(
        self,
        interaction_type: str,
        content: Any,
        skills_mentioned: Optional[List[str]] = None
    ):
        """从交互中学习"""
        self.profile_memory.add_interaction(interaction_type, content)

        if skills_mentioned:
            self.update_user_skills(skills_mentioned)

    def search_memory(self, keyword: str) -> List[Dict]:
        """搜索记忆"""
        results = []

        keyword_lower = keyword.lower()

        for skill_name in self.profile_memory.skill_profile.skills:
            if keyword_lower in skill_name.lower():
                results.append({
                    "type": "skill",
                    "content": skill_name
                })

        for note_key, note_content in self.profile_memory.notes.items():
            if keyword_lower in note_key.lower() or keyword_lower in note_content.lower():
                results.append({
                    "type": "note",
                    "key": note_key,
                    "content": note_content
                })

        return results

    def get_summary(self) -> Dict[str, Any]:
        """获取记忆摘要"""
        return {
            "user_id": self.user_id,
            "total_skills": len(self.profile_memory.skill_profile.skills),
            "top_skills": self.profile_memory.skill_profile.get_top_skills(5),
            "total_interactions": len(self.profile_memory.interaction_history),
            "achievements": list(self.profile_memory.achievements)
        }
