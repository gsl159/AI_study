# app/evidence/log_collector.py
from typing import Dict, Any

class LogCollector:
    def collect(self, raw_log: str) -> Dict[str, Any]:
        log_lower = str(raw_log).lower()
        if "permission" in log_lower:
            return {"error": "Permission denied", "confidence": 0.90}
        return {"error": "none", "confidence": 0.10}
