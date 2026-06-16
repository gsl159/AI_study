# app/evidence/metrics_collector.py
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
