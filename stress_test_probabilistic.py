# stress_test_probabilistic.py
import logging
from app.evidence.fusion_engine import EvidenceFusionEngine
from app.evidence.types import VerifiedEvidence, EvidenceSource
from app.executor.convergence import ConvergenceController
from app.executor.linux_executor import LinuxExecutor
from app.executor.base_executor import VerificationProbe, ActionType

# 设置日志格式以观察闭环过程
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("StressTest")

def run_p0_integration_test():
    # 1. 初始化系统组件
    engine = EvidenceFusionEngine()
    conv_ctrl = ConvergenceController(max_iters=6, threshold=0.92, min_delta=0.03)
    executor = LinuxExecutor()
    
    logger.info("================================================================================")
    logger.info("🔥 [P0 闭环] 自主诊断系统集成压测启动")
    logger.info("================================================================================")
    
    # 2. 初始诊断触发
    initial_hypotheses = engine.adjudicate_fault({"log": "Permission denied"})
    best_hypothesis = initial_hypotheses[0]
    logger.info(f"🚀 [Initial Rank] 假说: {best_hypothesis.cause} (Score: {best_hypothesis.score:.4f})")
    
    # 3. 进入闭环状态机
    current_confidence = best_hypothesis.score
    iteration = 0
    
    while conv_ctrl.should_continue(current_confidence):
        iteration += 1
        logger.info(f"\n--- 循环第 {iteration} 轮 (Confidence: {current_confidence:.4f}) ---")
        
        # 4. 模拟规划：生成探针 (在生产中这里由 VerificationPlanner 生成)
        probe = VerificationProbe(
            probe_id=f"P00{iteration}",
            target_hypothesis=best_hypothesis.cause,
            cmd="ls -ld /var/lib/mysql",
            action_type=ActionType.READ_ONLY,
            expected_evidence={"owner": "root"}
        )
        
        # 5. 执行：扣动物理扳机 (模拟物理返回)
        # 真实场景中，这里会调用 executor.execute(probe)
        raw_output = "drwxr-xr-x 2 root root 4096 Jun 16 2026 /var/lib/mysql"
        
        # 6. 证据提取与回灌 (VerifiedEvidence 结构化)
        new_evidence = VerifiedEvidence(
            evidence_type="filesystem_permission",
            source=EvidenceSource.PROBE_EXECUTION,
            value={"owner": "root", "raw": raw_output},
            confidence=0.95
        )
        
        # 7. 🔥 闭环核心：Evidence Feedback -> Re-Ranking
        new_rankings = engine.re_adjudicate(new_evidence)
        
        # 8. 更新收敛状态
        best_hypothesis = new_rankings[0]
        current_confidence = best_hypothesis.score
        
        logger.info(f"📊 [Re-Rank] {best_hypothesis.cause} -> Score: {current_confidence:.4f}")
        
    logger.info("\n================================================================================")
    logger.info(f"🏁 [STOP] 收敛逻辑触发: 诊断闭环结束。最终根因: {best_hypothesis.cause}")
    logger.info("================================================================================")

if __name__ == "__main__":
    run_p0_integration_test()
