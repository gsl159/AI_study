# app/evidence/ranker.py
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
