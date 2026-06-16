# app/evidence/rag_collector.py
from typing import Dict, Any

class RagCollector:
    def collect(self, error_context: str) -> Dict[str, Any]:
        if "permission" in str(error_context).lower():
            return {"matched_doc": "RUNBOOK-045", "confidence": 0.80}
        return {"matched_doc": "None", "confidence": 0.0}
