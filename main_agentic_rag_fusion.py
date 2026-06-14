# main_agentic_rag_fusion.py
import logging
from tool_registry import EnterpriseToolRegistry
from context_models import ChunkEntityV3, SectionContext
from budget_context_builder import BudgetContextBuilder
from agentic_brain import AgenticKnowledgeSystem

# 开启生产级高精密度时间轴日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

# ── 💡 模拟底层基础设施层暴露给工具表的原子函数（修复命名对齐） ───────────────────────
def mock_os_check_service(service_name): 
    return "mysqld -> STATUS: active(failed) since 10 min ago"

def mock_os_check_port(port_num): 
    return f"port {port_num} -> status: FREE"

# 🟢 修复点：确保此处的函数命名，与下方注册时传入的指针完全物理一致
def mock_os_verify_permission(): 
    return "ls -ld /var/lib/mysql -> drwxr-xr-x 2 root root (🚨 CRITICAL: Should be mysql:mysql)"


if __name__ == "__main__":
    print("="*70 + "\n🔥 LEVEL 3 终极合龙：Agentic Knowledge System 运行时全线拉起\n" + "="*70)

    # 1. 初始化自带中央无感监控拦截器的武器库
    registry = EnterpriseToolRegistry()

    # 2. 将 Linux 运维命令注册入武器库
    registry.register_tool("check_service", "查询本地服务存活状态", mock_os_check_service)
    registry.register_tool("check_port", "查询本地网络端口占用", mock_os_check_port)
    
    # 🟢 修复点：原本传入的 mock_os_check_permission 并不存在，现已完美修正为 mock_os_verify_permission
    registry.register_tool("verify_mysql_dir_permission", "物理查看MySQL数据目录的属主和属组权限", mock_os_verify_permission)

    # 3. 将 Level 2 终极 RAG + V3 Budget Builder 打包变成一个原子注册工具
    def integrated_rag_tool_facade(query: str, intent: str) -> str:
        """内部紧密咬合倒排索引和预算裁剪代码，在 Agent 武器库中作为历史经验燃料提供者"""
        mock_section = SectionContext(
            id="S2", 
            title="MySQL权限踩坑指南", 
            summary="核心讲解由于数据目录属主误变更为root导致守护进程无权写pid文件引发启动溃烂的排障历史经验。"
        )
        mock_chunk = ChunkEntityV3(
            id="C2_1", section_id="S2", order_index=0, score=0.99, 
            full_text="【工业级血泪案例】如果MySQL报错无法创建 PID 文件，99% 是因为执行了 sudo chown -R root:root /var/lib/mysql。正确修复方案是执行: chown -R mysql:mysql /var/lib/mysql 恢复生产。", 
            short_summary="目录被误改root权限导致crash"
        )
        
        # 激活 V3 Budget 裁剪器
        budget_精算师 = BudgetContextBuilder(max_context_budget=400)
        return budget_精算师.build_context(query_intent=intent, target_sections=[mock_section], recalled_chunks=[mock_chunk])

    # 将整个 RAG 帝国作为“一颗高能子弹”装进工具注册表中
    registry.register_tool("hybrid_retrieve_and_budget_build", "翻阅企业百万级历史高价值专家运维知识库资产", integrated_rag_tool_facade)

    # 4. 启动完全体 Agent 大脑
    agent_system = AgenticKnowledgeSystem(
        api_key="sk-68901eb2d2894926bb24442944c1eb23",
        base_url="https://api.deepseek.com/v1",
        model_name="deepseek-chat",
        tool_registry=registry
    )

    # 5. 发起复杂的黑天鹅故障诊断请求
    agent_system.run_diagnose(user_incident="线上DBA集群3号机节点突发死锁crash，重启后直接长眠，无法拉起。")

    print("\n" + "="*70 + "\n🏁 AGENTIC KNOWLEDGE SYSTEM 战报完整审计追踪看板\n" + "="*70)
    for idx, trail in enumerate(agent_system.audit_trail):
        print(f"  📜 [Step {idx+1}] {trail}")

    # ── 💡 6. 核心高光时刻：打印全链路无感拦截监控仪表盘 ─────────────────────────
    registry.print_production_dashboard()
