# stress_test_probabilistic.py
import logging
import os
import sys

# ==============================================================================
# 🧱 刚性路径重力对齐：不管你在哪个目录下执行，强行把 Level_0 锚定为绝对根路径
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 这就是 Level_0 的物理绝对路径
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR) # 强制插到第一位，拥有最高解释优先级

# 屏蔽第三方库（如 streamlit 残留组件）对当前命令行控制台的日志污染
logging.getLogger("streamlit").setLevel(logging.ERROR)

from production_memory_index import ProductionMemoryIndexBase
from app.evidence.fusion_engine import EvidenceFusionEngine
from memory_taxonomy import ProductionCaseMemory, RootCauseTaxonomy

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("L44-Architecture-Review")

def execute_probabilistic_audit():
    logger.info("================================================================================")
    logger.info("🔥 LEVEL 4.4 概率化诊断引擎：企业级动态加权、时间衰减与多假说评审对撞")
    logger.info("================================================================================")

    # 1. 初始化持久化长期记忆引擎
    memory_infra = ProductionMemoryIndexBase()
    
    # 2. 预埋一条一年前的陈旧案例
    case_old = ProductionCaseMemory(
        case_id="CASE-OLD-2025",
        taxonomy_cause=RootCauseTaxonomy.FS_PERMISSION_DENIED,
        raw_fingerprint_data={
            "service_status": "failed_inactive", "port_status": "free_none",
            "error_log": "Can't create pid file: Permission denied"
        },
        standard_fix_cmd="chown -R mysql:mysql /var/lib/mysql"
    )
    memory_infra.commit_production_case(case_old)
    
    # 3. 挂载 L4.4 级完备概率合流引擎
    probabilistic_engine = EvidenceFusionEngine(memory_engine=memory_infra)

    # --------------------------------------------------------------------------
    # 🔬 生产对撞测试一：同样的 Permission Denied，发生在一整年（365天）之后！
    # --------------------------------------------------------------------------
    logger.info("\n🚨 [场景测试一] 线上再次爆发 Permission denied 故障，但此时距离历史案例已过去 365 天...")
    
    log_p = "CRITICAL: dump runtime core state cluster failed, Local physical file IO blocked: Permission denied"
    metrics_p = {"cpu_usage": 12.5, "iowait": 42.0}
    trace_p = {"redis_latency": 15, "mysql_latency": 45}
    topology_p = {"service_status": "failed_inactive", "port_status": "free_none"}

    result_1 = probabilistic_engine.adjudicate_fault(
        raw_log=log_p, metrics_data=metrics_p, trace_data=trace_p,
        topology_features=topology_p, simulated_days_ago=365.0
    )

    logger.info("--------------------------------------------------------------------------------")
    logger.info("📝 场景一 概率化诊断大盘报告：")
    logger.info(f" ⚙️ 动态输出模态加权大盘 (Weights)   : {result_1['weights_applied']}")
    logger.info(f" 📊 因果假说排行榜 (Hypothesis Rank)  : {result_1['hypotheses_ranking']}")
    logger.info(f" 🛡️ 生成的主动非破坏性探针规划 (Probes) :")
    for plan in result_1['verification_plan']:
        logger.info(f"    ▶ [目标假说] {plan['target_hypothesis']} (期望得分: {plan['probabilistic_score']})")
        for p in plan['assigned_probes']:
            logger.info(f"       - 探针指令: {p['verify_cmd']} --> 期待匹配: {p['expected']}")

    # --------------------------------------------------------------------------
    # 🔬 生产对撞测试二：极致的分布式穿透案例 (日志静默、记忆真空)
    # --------------------------------------------------------------------------
    logger.info("\n🚨 [场景测试二] 爆发极端高并发黑天鹅故障，日志毫无报错，记忆库完全空白...")
    
    silent_log = "INFO: connection context established pool maintenance worker cycle idle"
    metrics_saturated = {"cpu_usage": 98.5, "iowait": 5.0}
    trace_blocked = {"redis_latency": 3850, "mysql_latency": 12}
    topology_active = {"service_status": "active_running", "port_status": "occupied_established"}

    result_2 = probabilistic_engine.adjudicate_fault(
        raw_log=silent_log, metrics_data=metrics_saturated, trace_data=trace_blocked,
        topology_features=topology_active, simulated_days_ago=0.0
    )

    logger.info("--------------------------------------------------------------------------------")
    logger.info("📝 场景二 概率化诊断大盘报告：")
    logger.info(f" ⚙️ 动态输出模态加权大盘 (Weights)   : {result_2['weights_applied']}")
    logger.info(f" 📊 因果假说排行榜 (Hypothesis Rank)  : {result_2['hypotheses_ranking']}")
    logger.info(f" 🛡️ 生成的主动非破坏性探针规划 (Probes) :")
    for plan in result_2['verification_plan']:
        logger.info(f"    ▶ [目标假说] {plan['target_hypothesis']} (期望得分: {plan['probabilistic_score']})")
        for p in plan['assigned_probes']:
            logger.info(f"       - 探针指令: {p['verify_cmd']} --> 期待匹配: {p['expected']}")
    logger.info("================================================================================")

if __name__ == "__main__":
    execute_probabilistic_audit()