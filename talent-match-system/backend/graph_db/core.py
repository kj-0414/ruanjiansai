import json
import os
from typing import Dict, List, Optional, Any

class LightweightGraphDB:
    """轻量级图数据库，用于存储能力树状图谱数据"""
    
    def __init__(self, db_path: str = "graph_data"):
        """初始化图数据库
        
        Args:
            db_path: 数据库文件存储路径
        """
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        self.nodes_file = os.path.join(self.db_path, "nodes.json")
        self.relationships_file = os.path.join(self.db_path, "relationships.json")
        self._init_files()
    
    def _init_files(self):
        """初始化数据库文件"""
        if not os.path.exists(self.nodes_file):
            with open(self.nodes_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        if not os.path.exists(self.relationships_file):
            with open(self.relationships_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_nodes(self) -> Dict[str, Dict[str, Any]]:
        """加载节点数据"""
        with open(self.nodes_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_nodes(self, nodes: Dict[str, Dict[str, Any]]):
        """保存节点数据"""
        with open(self.nodes_file, 'w', encoding='utf-8') as f:
            json.dump(nodes, f, ensure_ascii=False, indent=2)
    
    def _load_relationships(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载关系数据"""
        with open(self.relationships_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_relationships(self, relationships: Dict[str, List[Dict[str, Any]]]):
        """保存关系数据"""
        with open(self.relationships_file, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, ensure_ascii=False, indent=2)
    
    def create_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """创建节点
        
        Args:
            node_id: 节点ID
            properties: 节点属性
        
        Returns:
            bool: 是否创建成功
        """
        nodes = self._load_nodes()
        if node_id in nodes:
            return False
        nodes[node_id] = properties
        self._save_nodes(nodes)
        return True
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点
        
        Args:
            node_id: 节点ID
        
        Returns:
            Optional[Dict[str, Any]]: 节点属性
        """
        nodes = self._load_nodes()
        return nodes.get(node_id)
    
    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """更新节点
        
        Args:
            node_id: 节点ID
            properties: 节点属性
        
        Returns:
            bool: 是否更新成功
        """
        nodes = self._load_nodes()
        if node_id not in nodes:
            return False
        nodes[node_id].update(properties)
        self._save_nodes(nodes)
        return True
    
    def delete_node(self, node_id: str) -> bool:
        """删除节点
        
        Args:
            node_id: 节点ID
        
        Returns:
            bool: 是否删除成功
        """
        nodes = self._load_nodes()
        if node_id not in nodes:
            return False
        del nodes[node_id]
        self._save_nodes(nodes)
        
        # 删除相关关系
        relationships = self._load_relationships()
        if node_id in relationships:
            del relationships[node_id]
        # 删除以该节点为目标的关系
        for source_id, rels in list(relationships.items()):
            relationships[source_id] = [rel for rel in rels if rel['target'] != node_id]
        self._save_relationships(relationships)
        
        return True
    
    def create_relationship(self, source: str, target: str, relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """创建关系
        
        Args:
            source: 源节点ID
            target: 目标节点ID
            relationship_type: 关系类型
            properties: 关系属性
        
        Returns:
            bool: 是否创建成功
        """
        nodes = self._load_nodes()
        if source not in nodes or target not in nodes:
            return False
        
        relationships = self._load_relationships()
        if source not in relationships:
            relationships[source] = []
        
        # 检查关系是否已存在
        for rel in relationships[source]:
            if rel['target'] == target and rel['type'] == relationship_type:
                return False
        
        rel_data = {
            'target': target,
            'type': relationship_type
        }
        if properties:
            rel_data.update(properties)
        
        relationships[source].append(rel_data)
        self._save_relationships(relationships)
        return True
    
    def get_relationships(self, node_id: str, relationship_type: str = None) -> List[Dict[str, Any]]:
        """获取节点的关系
        
        Args:
            node_id: 节点ID
            relationship_type: 关系类型
        
        Returns:
            List[Dict[str, Any]]: 关系列表
        """
        relationships = self._load_relationships()
        if node_id not in relationships:
            return []
        
        if relationship_type:
            return [rel for rel in relationships[node_id] if rel['type'] == relationship_type]
        return relationships[node_id]
    
    def get_related_nodes(self, node_id: str, relationship_type: str = None) -> List[Dict[str, Any]]:
        """获取相关节点
        
        Args:
            node_id: 节点ID
            relationship_type: 关系类型
        
        Returns:
            List[Dict[str, Any]]: 相关节点列表
        """
        relationships = self.get_relationships(node_id, relationship_type)
        nodes = self._load_nodes()
        result = []
        
        for rel in relationships:
            target_id = rel['target']
            if target_id in nodes:
                node_data = nodes[target_id].copy()
                node_data['_id'] = target_id
                node_data['_relationship'] = rel
                result.append(node_data)
        
        return result
    
    def get_path(self, start_id: str, end_id: str, max_depth: int = 10) -> List[List[str]]:
        """获取两点之间的路径
        
        Args:
            start_id: 起始节点ID
            end_id: 目标节点ID
            max_depth: 最大深度
        
        Returns:
            List[List[str]]: 路径列表
        """
        def dfs(current: str, path: List[str], depth: int):
            if current == end_id:
                paths.append(path.copy())
                return
            if depth >= max_depth:
                return
            
            for rel in self.get_relationships(current):
                next_node = rel['target']
                if next_node not in path:
                    path.append(next_node)
                    dfs(next_node, path, depth + 1)
                    path.pop()
        
        paths = []
        dfs(start_id, [start_id], 0)
        return paths
    
    def query_nodes(self, properties: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查询节点
        
        Args:
            properties: 查询属性
        
        Returns:
            List[Dict[str, Any]]: 符合条件的节点
        """
        nodes = self._load_nodes()
        result = []
        
        for node_id, node_data in nodes.items():
            match = True
            for key, value in properties.items():
                if key not in node_data or node_data[key] != value:
                    match = False
                    break
            if match:
                node_copy = node_data.copy()
                node_copy['_id'] = node_id
                result.append(node_copy)
        
        return result
    
    def clear(self):
        """清空数据库"""
        self._save_nodes({})
        self._save_relationships({})

# 全局图数据库实例
graph_db = LightweightGraphDB(os.path.join(os.path.dirname(__file__), "data"))