# app/evidence/verification.py
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
