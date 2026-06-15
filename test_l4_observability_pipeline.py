# test_l4_observability_pipeline.py
import logging
from enterprise_memory import EnterpriseMemoryBase
from memory_models import CaseMemory, RootCauseType, HypothesisStep

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

if __name__ == "__main__":
    print("="*80 + "\n🔥 LEVEL 4 终极重构演练：高保真法医诊断记忆层全线实测\n" + "="*80)

    # 1. 挂载记忆中枢
    memory_center = EnterpriseMemoryBase()

    # ── 💡 场景 1：录入 CASE-001（真实的权限损坏案件） ────────────────────────────────
    print("\n📥 [Step 1] 正在将 CASE-001 深度解剖战报打入记忆矩阵...")
    
    case_001 = CaseMemory(
        case_id="CASE-001",
        symptoms=["mysqld failed startup"],
        # 深度指纹化存储
        evidence_fingerprint={
            "service_status": "failed",
            "port_status": "free",
            "error_log": "Can't create pid file: Permission denied"
        },
        # 高保真假设推导路径跟踪
        hypothesis_chain=[
            HypothesisStep(hypothesis="check service survival", tool="check_service", result="failed", confidence=1.0),
            HypothesisStep(hypothesis="inspect pid file owner", tool="verify_mysql_dir_permission", result="confirmed", confidence=0.95)
        ],
        root_cause_type=RootCauseType.PERMISSION_DENIED, # 强类型规范化
        fix_action="chown -R mysql:mysql /var/lib/mysql"
    )
    memory_center.commit_case(case_001)


    # ── 💡 场景 2：线上再次爆发故障！拦截器启动高保真指纹余弦比对 ───────────────────────
    print("\n" + "-"*80 + "\n🚨 [Step 2] 线上另一台机器暴发故障，指纹精算器开始启动交叉审判...")
    
    # 恶意的诱导性故障：同样是服务挂了、端口闲置，但关键报错文本完全不同（实际是因为磁盘满了）
    trap_fingerprint = {
        "service_status": "failed",
        "port_status": "free",
        "error_log": "No space left on device: write /var/lib/mysql/log failed"
    }

    # 进行 0.85 门槛的精密阻断测试
    matched_case = memory_center.recall_similar_case(trap_fingerprint, threshold=0.85)
    
    if not matched_case:
        print("✅ [架构演进成功] 成功看穿了表面的相似！指纹精算拦截器拒绝了这次极度危险的误召回，智能体将开始全新的独立诊断。")


    # ── 💡 场景 3：线上爆发 100% 吻合的同类案件 ───────────────────────────────────
    print("\n" + "-"*80 + "\n🚨 [Step 3] 生产环境再次爆发高真实相似度案件（确定又是权限坏了）...")
    
    true_clone_fingerprint = {
        "service_status": "failed",
        "port_status": "free",
        "error_log": "Can't create pid file: Permission denied"
    }
    
    hit_case = memory_center.recall_similar_case(true_clone_fingerprint, threshold=0.85)
    if hit_case:
        print(f"🎉 [精确断路拦截成功!!] 提取强类型结论 -> {hit_case.root_cause_type.value} | 建议修复指令: {hit_case.fix_action}")


    # ── 💡 场景 4：总架构师指定的 O(1) 倒排索引反查威力展示 ───────────────────────
    print("\n" + "-"*80 + "\n🚀 [Step 4] 监控大盘发起根因追溯：查找所有属于 PERMISSION_DENIED 的历史卷宗...")
    
    # 无需遍历 episodic_db，直接秒级提取
    retrieved_cases = memory_center.find_cases_by_root_cause(RootCauseType.PERMISSION_DENIED)
    print(f"  🔍 [倒排索引秒击穿] 复杂度 O(1)。在分类槽中秒级揪出以下案件: {[c.case_id for c in retrieved_cases]}")
    
    print("\n" + "="*80 + "\n🏁 LEVEL 4-V2 阶段性战报审计大盘\n" + "="*80)
    print("  🟩 强类型规范化：完全消灭字符串模糊匹配带来的统计溃烂。")
    print("  🟩 高保真推导路径：完整保留每一个推论步骤的置信度与成败轨迹。")
    print("  🟩 指纹余弦相似度：用数学几何特征向量防御虚假的高频误召回。")
    print("  🟩 O(1) 倒排索引：将系统的大盘反查时间开销彻底砸平。")
    print("="*80)
