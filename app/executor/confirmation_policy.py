# app/executor/confirmation_policy.py
from app.core.diagnostic_result import ConfirmationResult

class RootCauseConfirmationPolicy:
    MIN_CONFIDENCE = 0.92
    MIN_VERIFIED_EVIDENCE = 2
    MAX_CONFLICT_RATIO = 0.2

    @classmethod
    def evaluate(cls, confidence: float, verified_count: int, conflict_ratio: float) -> ConfirmationResult:
        if confidence >= cls.MIN_CONFIDENCE and verified_count >= cls.MIN_VERIFIED_EVIDENCE and conflict_ratio <= cls.MAX_CONFLICT_RATIO:
            return ConfirmationResult(True, "all_criteria_met", confidence)
        
        if verified_count >= 1 and confidence >= 0.7:
            return ConfirmationResult(False, "partially_confirmed", confidence)
            
        return ConfirmationResult(False, "insufficient_or_conflicting", confidence)
