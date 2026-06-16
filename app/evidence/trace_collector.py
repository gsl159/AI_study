# app/evidence/trace_collector.py
from typing import Dict, Any

class TraceCollector:
    def collect(self, trace_data: Dict[str, int]) -> Dict[str, Any]:
        redis_latency = trace_data.get("redis_latency", 0)
        if redis_latency > 3000:
            return {"trace_anomaly_type": "REDIS_TIMEOUT", "confidence": 0.95}
        return {"trace_anomaly_type": "NORMAL", "confidence": 0.15}
