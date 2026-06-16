# app/core/result_factory.py
from app.core.diagnostic_result import DiagnosticResult
from app.evidence.states import DiagnosticOutcome

class DiagnosticResultFactory:
    @staticmethod
    def confirmed(confidence, evidence_count, conflict_ratio, root_cause, iterations, time_ms, reasoning) -> DiagnosticResult:
        return DiagnosticResult(
            DiagnosticOutcome.ROOT_CAUSE_CONFIRMED,
            confidence, evidence_count, conflict_ratio, root_cause, iterations, time_ms, reasoning
        )
    
    @staticmethod
    def failed(reasoning, iterations, time_ms) -> DiagnosticResult:
        return DiagnosticResult(
            DiagnosticOutcome.FAILED_TO_CONFIRM, 0.0, 0, 0.0, None, iterations, time_ms, reasoning
        )
    # ... 其他静态方法：timeout, insufficient, aborted ...
