"""
技能知识图谱模块
基于 NetworkX 实现技能关系图谱
"""

import networkx as nx
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillKnowledgeGraph:
    """
    技能知识图谱类
    基于NetworkX实现技能关系网络
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.skill_attributes = {}
        self.occupation_attributes = {}
        self.relation_types = {
            'co_occurrence': '共现关系',
            'similar': '相似关系',
            'prerequisite': '前置技能',
            'same_category': '同类别',
            'required_for': '职业要求',
            'related_to': '相关技能'
        }

    def add_skill_node(self, skill_id: int, skill_info: Dict):
        """添加技能节点"""
        node_id = f"skill_{skill_id}"

        self.graph.add_node(node_id, **{
            'node_type': 'skill',
            'skill_id': skill_id,
            **skill_info
        })

        self.skill_attributes[skill_id] = skill_info

    def add_occupation_node(self, occupation_id: int, occupation_info: Dict):
        """添加职业节点"""
        node_id = f"occupation_{occupation_id}"

        self.graph.add_node(node_id, **{
            'node_type': 'occupation',
            'occupation_id': occupation_id,
            **occupation_info
        })

        self.occupation_attributes[occupation_id] = occupation_info

    def add_skill_relation(self, skill_id_1: int, skill_id_2: int,
                          relation_type: str, weight: float = 1.0,
                          metadata: Optional[Dict] = None):
        """添加技能之间的关系"""
        node_1 = f"skill_{skill_id_1}"
        node_2 = f"skill_{skill_id_2}"

        if not self.graph.has_node(node_1):
            self.add_skill_node(skill_id_1, {'skill_name': f'skill_{skill_id_1}'})

        if not self.graph.has_node(node_2):
            self.add_skill_node(skill_id_2, {'skill_name': f'skill_{skill_id_2}'})

        edge_data = {
            'relation_type': relation_type,
            'weight': weight,
            'created_at': datetime.now().isoformat()
        }

        if metadata:
            edge_data.update(metadata)

        if self.graph.has_edge(node_1, node_2):
            existing_weight = self.graph[node_1][node_2].get('weight', 0)
            edge_data['weight'] = max(existing_weight, weight)
            self.graph[node_1][node_2].update(edge_data)
        else:
            self.graph.add_edge(node_1, node_2, **edge_data)

    def add_skill_to_occupation(self, skill_id: int, occupation_id: int,
                               importance: float = 0.5, is_core: bool = False):
        """添加技能-职业关联"""
        skill_node = f"skill_{skill_id}"
        occ_node = f"occupation_{occupation_id}"

        if not self.graph.has_node(skill_node):
            self.add_skill_node(skill_id, {'skill_name': f'skill_{skill_id}'})

        if not self.graph.has_node(occ_node):
            self.add_occupation_node(occupation_id, {'level2_name': f'occupation_{occupation_id}'})

        self.graph.add_edge(skill_node, occ_node, **{
            'relation_type': 'required_for',
            'importance': importance,
            'is_core': is_core,
            'created_at': datetime.now().isoformat()
        })

    def get_related_skills(self, skill_id: int, max_depth: int = 2,
                           relation_type: Optional[str] = None) -> List[Dict]:
        """
        获取与指定技能相关的技能列表

        Args:
            skill_id: 技能ID
            max_depth: 最大遍历深度
            relation_type: 关系类型过滤

        Returns:
            相关技能列表，每个元素包含节点信息和距离
        """
        node = f"skill_{skill_id}"

        if not self.graph.has_node(node):
            logger.warning(f"技能节点不存在: {skill_id}")
            return []

        related = []
        visited = set()

        for neighbor, edge_data in self.graph[node].items():
            if neighbor.startswith('skill_'):
                if relation_type and edge_data.get('relation_type') != relation_type:
                    continue

                related.append({
                    'skill_id': int(neighbor.split('_')[1]),
                    'distance': 1,
                    'relation_type': edge_data.get('relation_type'),
                    'weight': edge_data.get('weight', 1.0),
                    **self.graph.nodes[neighbor]
                })
                visited.add(neighbor)

        if max_depth > 1 and relation_type is None:
            for neighbor in list(visited):
                for next_neighbor, edge_data in self.graph[neighbor].items():
                    if (next_neighbor.startswith('skill_') and
                        next_neighbor not in visited):

                        if edge_data.get('relation_type') == 'prerequisite':
                            continue

                        related.append({
                            'skill_id': int(next_neighbor.split('_')[1]),
                            'distance': 2,
                            'relation_type': edge_data.get('relation_type'),
                            'weight': edge_data.get('weight', 1.0) * 0.5,
                            **self.graph.nodes[next_neighbor]
                        })
                        visited.add(next_neighbor)

        related.sort(key=lambda x: (x['distance'], -x['weight']))

        return related

    def get_skill_learning_path(self, from_skill: int,
                                to_skill: int) -> Optional[List[Dict]]:
        """
        获取从源技能到目标技能的学习路径

        Args:
            from_skill: 起始技能ID
            to_skill: 目标技能ID

        Returns:
            学习路径列表，如果不存在路径则返回None
        """
        node_from = f"skill_{from_skill}"
        node_to = f"skill_{to_skill}"

        if not self.graph.has_node(node_from) or not self.graph.has_node(node_to):
            return None

        try:
            path = nx.shortest_path(self.graph, node_from, node_to)
            path_info = []

            for i, node in enumerate(path):
                node_data = self.graph.nodes[node]

                if i < len(path) - 1:
                    edge_data = self.graph[node][path[i+1]]
                    relation_type = edge_data.get('relation_type', 'related_to')
                else:
                    relation_type = 'target'

                path_info.append({
                    'step': i + 1,
                    'node_id': node,
                    'node_type': node_data.get('node_type'),
                    'name': node_data.get('skill_name') or node_data.get('level2_name'),
                    'relation_type': relation_type,
                    'weight': node_data.get('weight', 1.0) if node_data.get('node_type') == 'skill' else None,
                    **node_data
                })

            return path_info

        except nx.NetworkXNoPath:
            logger.warning(f"技能 {from_skill} 到 {to_skill} 之间不存在路径")
            return None

    def find_shortest_skill_path(self, skill_1: int, skill_2: int) -> Optional[List[int]]:
        """
        找到两个技能之间的最短路径（返回技能ID列表）

        Args:
            skill_1: 技能1 ID
            skill_2: 技能2 ID

        Returns:
            技能ID列表
        """
        node_1 = f"skill_{skill_1}"
        node_2 = f"skill_{skill_2}"

        try:
            path = nx.shortest_path(self.graph, node_1, node_2)
            return [int(node.split('_')[1]) for node in path]
        except nx.NetworkXNoPath:
            return None

    def get_skill_neighbors(self, skill_id: int,
                           neighbor_type: str = 'all') -> List[Dict]:
        """
        获取技能的直接邻居

        Args:
            skill_id: 技能ID
            neighbor_type: 'skill', 'occupation', 'all'

        Returns:
            邻居节点列表
        """
        node = f"skill_{skill_id}"

        if not self.graph.has_node(node):
            return []

        neighbors = []

        for neighbor, edge_data in self.graph[node].items():
            if neighbor_type == 'skill' and not neighbor.startswith('skill_'):
                continue
            elif neighbor_type == 'occupation' and not neighbor.startswith('occupation_'):
                continue

            neighbors.append({
                'node_id': neighbor,
                'relation_type': edge_data.get('relation_type'),
                'weight': edge_data.get('weight', 1.0),
                **self.graph.nodes[neighbor]
            })

        return neighbors

    def calculate_skill_similarity(self, skill_id_1: int,
                                   skill_id_2: int) -> float:
        """
        计算两个技能的相似度（基于共同邻居）

        Args:
            skill_id_1: 技能1 ID
            skill_id_2: 技能2 ID

        Returns:
            相似度分数 (0-1)
        """
        node_1 = f"skill_{skill_id_1}"
        node_2 = f"skill_{skill_id_2}"

        if not self.graph.has_node(node_1) or not self.graph.has_node(node_2):
            return 0.0

        neighbors_1 = set(self.graph.predecessors(node_1)) | set(self.graph.successors(node_1))
        neighbors_2 = set(self.graph.predecessors(node_2)) | set(self.graph.successors(node_2))

        if not neighbors_1 or not neighbors_2:
            return 0.0

        intersection = neighbors_1 & neighbors_2
        union = neighbors_1 | neighbors_2

        return len(intersection) / len(union) if union else 0.0

    def get_most_connected_skills(self, limit: int = 20) -> List[Dict]:
        """
        获取连接度最高的技能

        Args:
            limit: 返回数量限制

        Returns:
            技能列表
        """
        degree_dict = dict(self.graph.degree())

        skill_degrees = [
            (node, degree)
            for node, degree in degree_dict.items()
            if node.startswith('skill_')
        ]

        skill_degrees.sort(key=lambda x: x[1], reverse=True)

        result = []
        for node, degree in skill_degrees[:limit]:
            skill_info = {
                'skill_id': int(node.split('_')[1]),
                'degree': degree,
                **self.graph.nodes[node]
            }
            result.append(skill_info)

        return result

    def find_cliques(self, min_size: int = 3) -> List[List[int]]:
        """
        找到技能群体（完全子图）

        Args:
            min_size: 最小群体大小

        Returns:
            技能群体列表
        """
        undirected_graph = self.graph.to_undirected()

        cliques = list(nx.find_cliques(undirected_graph))

        skill_cliques = [
            [int(node.split('_')[1]) for node in clique]
            for clique in cliques
            if len(clique) >= min_size and all(n.startswith('skill_') for n in clique)
        ]

        return skill_cliques

    def get_skill_graph_stats(self) -> Dict:
        """获取图谱统计信息"""
        skill_nodes = [n for n in self.graph.nodes() if n.startswith('skill_')]
        occupation_nodes = [n for n in self.graph.nodes() if n.startswith('occupation_')]

        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'skill_nodes': len(skill_nodes),
            'occupation_nodes': len(occupation_nodes),
            'density': nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0,
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
                           if self.graph.number_of_nodes() > 0 else 0,
            'is_connected': nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False
        }

    def save_graph(self, filepath: Optional[str] = None):
        """保存图谱到文件"""
        if filepath is None:
            data_dir = Path(__file__).parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            filepath = str(data_dir / "skill_graph.gpickle")

        nx.write_gpickle(self.graph, filepath)
        logger.info(f"✅ 图谱已保存到: {filepath}")

        graph_info = self.get_skill_graph_stats()
        graph_info['last_updated'] = datetime.now().isoformat()

        info_path = str(Path(filepath).parent / "graph_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(graph_info, f, ensure_ascii=False, indent=2)

    def load_graph(self, filepath: Optional[str] = None) -> bool:
        """从文件加载图谱"""
        if filepath is None:
            data_dir = Path(__file__).parent / "data"
            filepath = str(data_dir / "skill_graph.gpickle")

        filepath = Path(filepath)

        if not filepath.exists():
            logger.warning(f"图谱文件不存在: {filepath}")
            return False

        try:
            self.graph = nx.read_gpickle(filepath)
            logger.info(f"✅ 图谱已从 {filepath} 加载")
            return True
        except Exception as e:
            logger.error(f"❌ 加载图谱失败: {e}")
            return False

    def to_networkx_graph(self) -> nx.DiGraph:
        """返回NetworkX图对象"""
        return self.graph

    def get_subgraph_by_skills(self, skill_ids: List[int]) -> nx.DiGraph:
        """
        获取指定技能及其关系的子图

        Args:
            skill_ids: 技能ID列表

        Returns:
            子图
        """
        nodes = [f"skill_{sid}" for sid in skill_ids if f"skill_{sid}" in self.graph.nodes()]

        for node in nodes:
            nodes.extend(self.graph.predecessors(node))
            nodes.extend(self.graph.successors(node))

        nodes = list(set(nodes))

        return self.graph.subgraph(nodes).copy()
