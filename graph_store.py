# graph_store.py
import logging
from typing import List, Dict, Tuple, Set
from graph_models import GraphNode, GraphEdge

logger = logging.getLogger("RAG-Graph-Store")

class EnterpriseGraphStore:
    """
    遵循架构师V4指令：独立、轻量级高性能内存图存储器
    利用双向邻接表实现 O(1) 级别的邻居节点穿透与拓扑扩散
    """
    def __init__(self):
        # 三大核心倒排索引表
        self.node_index: Dict[str, GraphNode] = {}
        self.outgoing_edges: Dict[str, List[Tuple[str, str]]] = {} # source_id -> [(target_id, relation)]
        self.incoming_edges: Dict[str, List[Tuple[str, str]]] = {} # target_id -> [(source_id, relation)]

    def add_node(self, node: GraphNode):
        self.node_index[node.id] = node
        if node.id not in self.outgoing_edges: self.outgoing_edges[node.id] = []
        if node.id not in self.incoming_edges: self.incoming_edges[node.id] = []

    def add_edge(self, edge: GraphEdge):
        # 自动补全可能遗漏的节点
        if edge.source_id not in self.node_index: self.add_node(GraphNode(id=edge.source_id, type="GENERIC", name=edge.source_id))
        if edge.target_id not in self.node_index: self.add_node(GraphNode(id=edge.target_id, type="GENERIC", name=edge.target_id))
        
        # 挂载正向邻接表（出度）
        self.outgoing_edges[edge.source_id].append((edge.target_id, edge.relation))
        # 挂载反向邻接表（入度，为未来的根因分析、排障逆向追溯做架构预留）
        self.incoming_edges[edge.target_id].append((edge.source_id, edge.relation))

    def get_neighbors(self, node_id: str, relation_filter: str = None) -> List[Tuple[str, str]]:
        """O(1) 获取当前节点的一跳（1-Hop）直接邻居与关系"""
        if node_id not in self.outgoing_edges:
            return []
        all_edges = self.outgoing_edges[node_id]
        if relation_filter:
            return [edge for edge in all_edges if edge[1] == relation_filter]
        return all_edges

    def expand_subgraph(self, start_node_id: str, max_hops: int = 2) -> Dict[str, List[str]]:
        """
        核心图扩散算法 (Graph Expansion)
        从起始实体出发，顺着依赖链条进行广度优先搜索 (BFS)，一口气挖出上下游拓扑血缘关系
        """
        logger.info(f"🕸️ [Graph Expansion] 启动图拓扑扩散。起点: '{start_node_id}' | 最大跳数: {max_hops}")
        
        visited_nodes: Set[str] = {start_node_id}
        queue: List[Tuple[str, int]] = [(start_node_id, 0)] # (node_id, current_hop)
        
        # 沉淀结构：relation -> [target_names]
        topology_results: Dict[str, List[str]] = {}

        while queue:
            curr_node_id, curr_hop = queue.pop(0)
            if curr_hop >= max_hops:
                continue
                
            neighbors = self.get_neighbors(curr_node_id)
            for neighbor_id, relation in neighbors:
                # 收集图资产数据
                if relation not in topology_results:
                    topology_results[relation] = []
                
                neighbor_name = self.node_index[neighbor_id].name
                if neighbor_name not in topology_results[relation]:
                    topology_results[relation].append(neighbor_name)
                
                # 继续向更深层扩散
                if neighbor_id not in visited_nodes:
                    visited_nodes.add(neighbor_id)
                    queue.append((neighbor_id, curr_hop + 1))
                    
        logger.info(f"✅ [Graph Expansion] 扩散完毕。共捕获 {len(topology_results)} 种拓扑关联类别。")
        return topology_results
