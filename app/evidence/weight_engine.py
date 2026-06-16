# app/evidence/weight_engine.py
from typing import Dict, Any

class WeightStrategyEngine:
    def calculate_weights(self, log_ev: Dict, metrics_v: Dict, trace_v: Dict, rag_v: Dict, has_mem: bool) -> Dict[str, float]:
        if metrics_v.get("confidence", 0.0) > 0.80 and metrics_v.get("metric_anomaly_type") == "CPU_SATURATED":
            return {"metrics": 0.55, "memory": 0.10, "logs": 0.15, "traces": 0.15, "rag": 0.05}
        if "permission" in str(log_ev.get("error", "")).lower():
            return {"logs": 0.45, "metrics": 0.15, "traces": 0.15, "memory": 0.20, "rag": 0.05}
        return {"memory": 0.20, "metrics": 0.25, "logs": 0.25, "traces": 0.20, "rag": 0.10}
