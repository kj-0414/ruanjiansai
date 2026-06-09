"""
向量数据库服务
用于技能语义搜索和相似度匹配
"""

import os
from typing import List, Dict, Any, Optional
import logging

import chromadb
from chromadb.config import Settings

try:
    from chromadb.utils import embedding_functions
    HAS_EMBEDDING = True
except ImportError:
    HAS_EMBEDDING = False
    logger.warning("sentence-transformers not available, using default embedding")

from modules.common import get_settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """向量数据库服务"""
    
    _instance: Optional['VectorDatabase'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._available = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        settings = get_settings()
        self._db_path = os.path.join(settings.kb_data_path, "vector_db")
        os.makedirs(self._db_path, exist_ok=True)
        
        try:
            self._client = chromadb.PersistentClient(
                path=self._db_path,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
            
            if HAS_EMBEDDING:
                self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            else:
                self._embedding_fn = None
            
            self._collection = self._client.get_or_create_collection(
                name="skills",
                embedding_function=self._embedding_fn if HAS_EMBEDDING else None,
                metadata={"hnsw:space": "cosine"}
            )
            
            self._initialized = True
            self._available = HAS_EMBEDDING
            if HAS_EMBEDDING:
                logger.info(f"Vector database initialized at {self._db_path}")
            else:
                logger.info(f"Vector database initialized without embedding (sentence-transformers not available)")
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            logger.info("Vector database disabled due to initialization error")
            self._initialized = True
            self._available = False
            self._client = None
            self._collection = None
    
    def is_available(self) -> bool:
        """检查向量数据库是否可用"""
        return self._available
    
    def add_skills(self, skills: List[Dict[str, Any]]) -> None:
        """
        添加技能到向量数据库
        
        Args:
            skills: 技能列表，每个技能包含 id, name, description
        """
        if not skills:
            return
        
        ids = [str(skill["id"]) for skill in skills]
        documents = [skill.get("description", skill["name"]) for skill in skills]
        metadatas = [
            {
                "name": skill["name"],
                "category": skill.get("category", ""),
                "parent_id": skill.get("parent_id", ""),
                "related_skills": skill.get("related_skills", [])
            }
            for skill in skills
        ]
        
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(skills)} skills to vector database")
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        语义搜索相似技能
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
        
        Returns:
            相似技能列表，包含技能名称、相似度分数和元数据
        """
        if not query.strip():
            return []
        
        if not self._available:
            logger.warning("Vector search not available")
            return []
        
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            matches = []
            for i in range(len(results["ids"][0])):
                matches.append({
                    "id": results["ids"][0][i],
                    "name": results["metadatas"][0][i]["name"],
                    "category": results["metadatas"][0][i]["category"],
                    "score": 1 - results["distances"][0][i],  # 转换为相似度
                    "description": results["documents"][0][i]
                })
            
            return sorted(matches, key=lambda x: x["score"], reverse=True)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def search_by_name(self, name: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        按名称搜索相似技能
        
        Args:
            name: 技能名称
            threshold: 相似度阈值
        
        Returns:
            匹配的技能列表
        """
        results = self.search_similar(name, top_k=10)
        return [r for r in results if r["score"] >= threshold]
    
    def get_skill_by_id(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取技能
        
        Args:
            skill_id: 技能ID
        
        Returns:
            技能信息，如果不存在返回None
        """
        try:
            results = self._collection.get(ids=[skill_id])
            if results["ids"]:
                return {
                    "id": results["ids"][0],
                    "name": results["metadatas"][0]["name"],
                    "category": results["metadatas"][0]["category"],
                    "description": results["documents"][0]
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get skill by id: {e}")
            return None
    
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """
        获取所有技能
        
        Returns:
            所有技能列表
        """
        try:
            results = self._collection.get()
            skills = []
            for i in range(len(results["ids"])):
                skills.append({
                    "id": results["ids"][i],
                    "name": results["metadatas"][i]["name"],
                    "category": results["metadatas"][i]["category"],
                    "description": results["documents"][i]
                })
            return skills
        except Exception as e:
            logger.error(f"Failed to get all skills: {e}")
            return []
    
    def count(self) -> int:
        """获取技能数量"""
        return self._collection.count()
    
    def clear(self) -> None:
        """清空向量数据库"""
        self._collection.delete(ids=self._collection.get()["ids"])
        logger.info("Vector database cleared")


def get_vector_db() -> VectorDatabase:
    """获取向量数据库单例"""
    return VectorDatabase()
