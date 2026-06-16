# fix_all.py
import os

print("🔥 开始全量编织 Level 4.4 概率化诊断引擎的所有物理组件...")

# 1. 刚性创建物理目录
os.makedirs("app/evidence", exist_ok=True)

# 2. 写入 Python 包契约哨兵
with open("app/__init__.py", "w", encoding="utf-8") as f:
    f.write("# app initialization\n")
with open("app/evidence/__init__.py", "w", encoding="utf-8") as f:
    f.write("# app.evidence initialization\n")

# 3. 全量写入 4 个多模态采集器
with open("app/evidence/log_collector.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/log_collector.py
from typing import Dict, Any

class LogCollector:
    def collect(self, raw_log: str) -> Dict[str, Any]:
        log_lower = str(raw_log).lower()
        if "permission" in log_lower:
            return {"error": "Permission denied", "confidence": 0.90}
        return {"error": "none", "confidence": 0.10}
''')

with open("app/evidence/metrics_collector.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/metrics_collector.py
from typing import Dict, Any

class MetricsCollector:
    def collect(self, metrics_data: Dict[str, float]) -> Dict[str, Any]:
        cpu = metrics_data.get("cpu_usage", 0.0)
        iowait = metrics_data.get("iowait", 0.0)
        if cpu > 90:
            return {"metric_anomaly_type": "CPU_SATURATED", "confidence": 0.95}
        if iowait > 40:
            return {"metric_anomaly_type": "IO_BOTTLE_NECK", "confidence": 0.85}
        return {"metric_anomaly_type": "NORMAL", "confidence": 0.10}
''')

with open("app/evidence/trace_collector.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/trace_collector.py
from typing import Dict, Any

class TraceCollector:
    def collect(self, trace_data: Dict[str, int]) -> Dict[str, Any]:
        redis_latency = trace_data.get("redis_latency", 0)
        if redis_latency > 3000:
            return {"trace_anomaly_type": "REDIS_TIMEOUT", "confidence": 0.95}
        return {"trace_anomaly_type": "NORMAL", "confidence": 0.15}
''')

with open("app/evidence/rag_collector.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/rag_collector.py
from typing import Dict, Any

class RagCollector:
    def collect(self, error_context: str) -> Dict[str, Any]:
        if "permission" in str(error_context).lower():
            return {"matched_doc": "RUNBOOK-045", "confidence": 0.80}
        return {"matched_doc": "None", "confidence": 0.0}
''')

# 4. 写入自适应动态权重引擎
with open("app/evidence/weight_engine.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/weight_engine.py
from typing import Dict, Any

class WeightStrategyEngine:
    def calculate_weights(self, log_ev: Dict, metrics_v: Dict, trace_v: Dict, rag_v: Dict, has_mem: bool) -> Dict[str, float]:
        if metrics_v.get("confidence", 0.0) > 0.80 and metrics_v.get("metric_anomaly_type") == "CPU_SATURATED":
            return {"metrics": 0.55, "memory": 0.10, "logs": 0.15, "traces": 0.15, "rag": 0.05}
        if "permission" in str(log_ev.get("error", "")).lower():
            return {"logs": 0.45, "metrics": 0.15, "traces": 0.15, "memory": 0.20, "rag": 0.05}
        return {"memory": 0.20, "metrics": 0.25, "logs": 0.25, "traces": 0.20, "rag": 0.10}
''')

# 5. 写入多假说概率排序器
with open("app/evidence/ranker.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/ranker.py
from typing import Dict, List, Any

class HypothesisRanker:
    def rank_hypotheses(self, evidences: Dict[str, Any], weights: Dict[str, float]) -> List[Dict[str, Any]]:
        log_ev = evidences["log"]
        mem_score = evidences["memory_score"]
        rag_ev = evidences["rag"]
        metric_ev = evidences["metrics"]
        trace_ev = evidences["trace"]
        
        ranked_list = []
        
        # 假说 1: 权限配置错误
        s_permission = (
            weights["logs"] * (0.90 if "Permission" in log_ev["error"] else 0.10) +
            weights["memory"] * mem_score +
            weights["rag"] * rag_ev["confidence"]
        )
        ranked_list.append({"cause": "INFRA_FS_PERMISSION_DENIED", "score": round(s_permission, 4)})

        # 假说 2: SELinux 静默拦截
        s_selinux = (
            weights["logs"] * (0.80 if "Permission" in log_ev["error"] else 0.10) +
            weights["memory"] * (mem_score * 0.5)
        )
        ranked_list.append({"cause": "SYSTEM_SELINUX_BLOCKED", "score": round(s_selinux, 4)})

        # 假说 3: 分布式容量与资源倾轧
        s_resource = (
            weights["metrics"] * (0.95 if metric_ev["metric_anomaly_type"] == "CPU_SATURATED" else 0.10) +
            weights["traces"] * (0.95 if trace_ev["trace_anomaly_type"] == "REDIS_TIMEOUT" else 0.10)
        )
        ranked_list.append({"cause": "DISTRIBUTED_RESOURCE_COMPLETION_BLOCKED", "score": round(s_resource, 4)})
        
        ranked_list.sort(key=lambda x: x["score"], reverse=True)
        return ranked_list
''')

# 6. 写入自动化探针规划器
with open("app/evidence/verification.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/verification.py
from typing import Dict, List, Any

class VerificationPlanner:
    def __init__(self):
        self.runbook_registry = {
            "INFRA_FS_PERMISSION_DENIED": [{"step": 1, "verify_cmd": "ls -ld /var/lib/mysql", "expected": "mysql:mysql"}],
            "SYSTEM_SELINUX_BLOCKED": [{"step": 1, "verify_cmd": "sestatus", "expected": "enforcing"}],
            "DISTRIBUTED_RESOURCE_COMPLETION_BLOCKED": [{"step": 1, "verify_cmd": "top -b -n 1", "expected": "cpu_high"}]
        }

    def generate_plan(self, ranked_hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        v_plans = []
        for item in ranked_hypotheses[:2]:
            cause = item["cause"]
            if item["score"] >= 0.15 and cause in self.runbook_registry:
                v_plans.append({
                    "target_hypothesis": cause,
                    "probabilistic_score": item["score"],
                    "assigned_probes": self.runbook_registry[cause]
                })
        return v_plans
''')

# 7. 写入完全限定路径的融合引擎核心
with open("app/evidence/fusion_engine.py", "w", encoding="utf-8") as f:
    f.write('''# app/evidence/fusion_engine.py
import logging
import math
from typing import Dict, Any

from app.evidence.log_collector import LogCollector
from app.evidence.metrics_collector import MetricsCollector
from app.evidence.trace_collector import TraceCollector
from app.evidence.rag_collector import RagCollector
from app.evidence.weight_engine import WeightStrategyEngine
from app.evidence.ranker import HypothesisRanker
from app.evidence.verification import VerificationPlanner

from production_memory_index import ProductionMemoryIndexBase

logger = logging.getLogger("Enterprise-Evidence-Engine")

class EvidenceFusionEngine:
    def __init__(self, memory_engine: ProductionMemoryIndexBase):
        self.memory_engine = memory_engine
        self.weight_engine = WeightStrategyEngine()
        self.ranker = HypothesisRanker()
        self.planner = VerificationPlanner()

    def adjudicate_fault(self, raw_log: str, metrics_data: Dict[str, float], trace_data: Dict[str, int], topology_features: Dict[str, str], simulated_days_ago: float = 0.0) -> Dict[str, Any]:
        logger.info("⚖️ [L4.4 Engine] 多模态分布式证据层收集启动...")
        log_ev = LogCollector().collect(raw_log)
        metric_ev = MetricsCollector().collect(metrics_data)
        trace_ev = TraceCollector().collect(trace_data)
        rag_ev = RagCollector().collect(raw_log)

        memory_score = 0.0
        has_memory = False
        memory_ctx = {"service_status": topology_features.get("service_status", "unknown"), "port_status": topology_features.get("port_status", "unknown"), "error_log": raw_log}
        
        memory_hit = self.memory_engine.fast_path_lsh_recall(memory_ctx)
        if memory_hit:
            has_memory = True
            similarity = 0.92 
            historical_success_rate = 0.87
            freshness_factor = math.exp(-simulated_days_ago / 90.0)
            memory_score = similarity * historical_success_rate * freshness_factor
            logger.info(f"💾 撞中历史案例 {memory_hit.case_id}。时间衰减因子: {freshness_factor:.4f}")

        dynamic_weights = self.weight_engine.calculate_weights(log_ev, metric_ev, trace_ev, rag_ev, has_mem=has_memory)
        evidences_pack = {"log": log_ev, "metrics": metric_ev, "trace": trace_ev, "rag": rag_ev, "memory_score": memory_score}
        ranked_hypotheses = self.ranker.rank_hypotheses(evidences_pack, dynamic_weights)
        verification_plan = self.planner.generate_plan(ranked_hypotheses)

        return {"weights_applied": dynamic_weights, "hypotheses_ranking": ranked_hypotheses, "verification_plan": verification_plan}
''')

print("💎 [成功] 全套 7 个子组件物理文件已全部落盘！物理拓扑彻底闭环。")