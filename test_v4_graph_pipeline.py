# test_v4_graph_pipeline.py
import logging
from graph_models import GraphNode, GraphEdge
from graph_store import EnterpriseGraphStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

if __name__ == "__main__":
    # 1. 初始化独立的图存储引擎
    graph_db = EnterpriseGraphStore()

    # 2. 注入高价值的企业 IT 基础架构拓扑节点
    nodes = [
        GraphNode(id="mysql", type="COMPONENT", name="MySQL 8.0 数据库"),
        GraphNode(id="linux", type="OS", name="Ubuntu 22.04 LTS 操作系统"),
        GraphNode(id="firewall", type="NETWORK", name="UFW 安全防火墙组"),
        GraphNode(id="storage", type="STORAGE", name="Ceph SSD 分布式持久化块存储"),
        GraphNode(id="network", type="NETWORK", name="VPC 虚拟私有云网络")
    ]
    for node in nodes: graph_db.add_node(node)

    # 3. 编织复杂的依赖与 requires 拓扑有向边网
    edges = [
        GraphEdge(source_id="mysql", target_id="linux", relation="depends_on"),
        GraphEdge(source_id="mysql", target_id="firewall", relation="depends_on"),
        GraphEdge(source_id="mysql", target_id="storage", relation="requires"),
        GraphEdge(source_id="firewall", target_id="network", relation="configures_on"),
        GraphEdge(source_id="storage", target_id="network", relation="configures_on")
    ]
    for edge in edges: graph_db.add_edge(edge)

    print("="*60 + "\n📥 STEP 1: 离线图存储库初始化成功，拓扑边网络构建完毕\n" + "="*60)

    # 4. ── 模拟在线端混合检索流程（Hybrid Retrieval） ─────────────────────
    user_query = "领导让我今天在生产环境部署一套MySQL，我到底需要提前申请和准备哪些组件、系统和资源？"
    print(f"🔍 用户提问: '{user_query}'")
    
    # 传统 RAG 会去向量库里苦苦搜寻“MySQL安装步骤.md”的纯文本片段。
    # 💡 而我们的 V4 Hybrid 引擎并行唤醒了图扩散处理器：
    print("\n" + "="*60 + "\n🧠 STEP 2: 唤醒图扩散推理引擎（Graph Hops Expansion）\n" + "="*60)
    
    # 假设系统实体识别（Entity Extraction）从句子里抓出了核心词 "mysql"
    target_entity = "mysql"
    
    # 顺着依赖网络向下无情扩散 2 跳（2-Hops BFS），把隐藏在幕后的基础设施一网打尽！
    knowledge_topology = graph_db.expand_subgraph(start_node_id=target_entity, max_hops=2)

    # 5. 将图谱推理出的确定性硬核依赖，优雅地合并到交付给 LLM 的上下文大礼包中
    print("\n" + "="*60 + "\n🏁 STEP 3: 图谱推理出的高纯度知识网（输送给 Context Builder）\n" + "="*60)
    
    print("【🔥 系统通过知识图谱自动推导出的依赖血缘网】:")
    for relation, entities in knowledge_topology.items():
        print(f"  ➡️ 关系类型 [{relation}] -> 涉及关联的基础设施实体: {', '.join(entities)}")
