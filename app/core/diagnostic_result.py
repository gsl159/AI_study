# app/core/diagnostic_result.py
from dataclasses import dataclass
from typing import Optional
from app.evidence.states import DiagnosticOutcome

@dataclass
class ConfirmationResult:
    confirmed: bool
    reason: str
    confidence: float

@dataclass
class DiagnosticResult:
    outcome: DiagnosticOutcome
    confidence: float
    verified_evidence_count: int
    conflict_ratio: float
    root_cause: Optional[str]
    iterations: int
    execution_time_ms: float
    reasoning: str
