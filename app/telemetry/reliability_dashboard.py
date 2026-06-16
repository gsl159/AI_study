# app/telemetry/reliability_dashboard.py
from dataclasses import dataclass, field
from collections import Counter
import statistics

from app.evidence.states import DiagnosticOutcome

@dataclass
class ReliabilityDashboard:
    # ... 已有的计数器 ...
    confidence_history: list = field(default_factory=list)
    execution_times: list = field(default_factory=list)

    def report(self):
        return {
            "success_rate": self._calc_rate(DiagnosticOutcome.ROOT_CAUSE_CONFIRMED),
            "avg_confidence": statistics.mean(self.confidence_history) if self.confidence_history else 0,
            "avg_execution_time_ms": statistics.mean(self.execution_times) if self.execution_times else 0,
            # ... 其他指标 ...
        }
