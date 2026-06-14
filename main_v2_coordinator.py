# main_v2_coordinator.py
import logging
from router_service import EnterpriseQueryRouter
from storage_engine import EnterpriseKnowledgeStore
from retrieval_engine import EnterpriseRetrievalEngine, RetrievalMode

# 打开高精度运维日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

# 模拟一份录入企业高价值知识库的 Markdown 资产
MOCK_DBA_DOCUMENT = """# 企业级 MySQL 8.0 核心运维大纲

## 1. 架构总览
介绍分布式数据库集群的拓扑关系，包含 MHA 架构与 Master-Slave 复制延迟优化。

## 2. 生产环境安装MySQL步骤
Step1：下载官方提供的规范化 rpm 包。
Step2：运行 yum install mysql-community-server 进行静默安装。
Step3：执行 systemctl start mysqld 唤醒数据库守护进程。
Step4：通过 grep temporary password 捞取初始随机密码并登录。

## 3. 核心参数my.cnf配置
生产环境必须在 /etc/my.cnf 中卡死以下硬核参数：
[mysqld]
port=3306
max_connections=5000
innodb_buffer_pool_size=16G
"""

if __name__ == "__main__":
    # 1. 离线摄入流启动：初始化我们的多级倒排索引库
    print("="*60 + "\n📥 STEP 1: 启动离线摄入流（Data Ingestion Pipeline）\n" + "="*60)
    kv_store = EnterpriseKnowledgeStore(chunk_size=60, overlap=10)
    doc_id = kv_store.add_document(doc_title="MySQL_Ops_Standard.md", raw_markdown=MOCK_DBA_DOCUMENT)
    print(f"📊 摄入成功！当前内存库中总计管辖了 {len(kv_store.section_index)} 个 Section，{len(kv_store.chunk_index)} 个物理 Chunks。")

    # 2. 初始化在线控制面：四层立体防御路由器与检索引擎
    router = EnterpriseQueryRouter(
        api_key="sk-68901eb2d2894926bb24442944c1eb23", base_url="https://api.deepseek.com/v1", model_name="deepseek-chat"
    )
    retrieval_engine = EnterpriseRetrievalEngine(store=kv_store)

    # 3. ── 场景模拟：用户发起了一个硬核的“流程问答” ───────────────────────
    print("\n" + "="*60 + "\n🏃 STEP 2: 模拟线上真实高并发请求（Procedure Query 流程检索）\n" + "="*60)
    user_query = "兄弟们，帮我看下在Linux上到底怎么一步步把MySQL安装并部署起来？"
    
    # 4. 经过四层防护网识别意图
    router_output = router.route(user_query)
    
    # 5. 💡 完美的战略合龙：将意图映射到你的 RetrievalMode 状态机
    # 映射字典（将人类的意图，转化为底层系统检索的分流开关）
    intent_to_mode_mapping = {
        "PROCEDURE": RetrievalMode.SECTION,    # 流程问答 -> 激活高价值 Section 连续召回线！
        "FACT_QA": RetrievalMode.CHUNK,        # 事实问答 -> 精准拉取叶子单片
        "CONFIGURATION": RetrievalMode.CHUNK,   # 配置参数 -> 也是精准叶子单片
        "TROUBLESHOOTING": RetrievalMode.HYBRID # 排障问答 -> 混合召回
    }
    
    # 动态分流
    chosen_mode = intent_to_mode_mapping.get(router_output.intent, RetrievalMode.CHUNK)
    
    # 6. 检索引擎接棒，进行确定性按序拼装
    final_recalled_chunks = retrieval_engine.retrieve(user_query, chosen_mode)
    
    # 7. 最终交付给 Context Builder 的大合拢展现
    print("\n" + "="*60 + "\n🏁 STEP 3: 最终交付给 Context Builder 的高价值资产看板\n" + "="*60)
    print(f"🎯 最终召回切片数量: {len(final_recalled_chunks)} 个")
    for chk in final_recalled_chunks:
        print(f"  --> [有序切片] ID: {chk.id} | Order_Idx: {chk.order_index} | 内容: {repr(chk.content)}")
