# app/evidence/states.py
from enum import Enum

class EvidenceState(Enum):
    VERIFIED = "verified"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"
    UNKNOWN = "unknown"

class DiagnosticOutcome(Enum):
    ROOT_CAUSE_CONFIRMED = "root_cause_confirmed"
    FAILED_TO_CONFIRM = "failed_to_confirm"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    EXECUTION_ABORTED = "execution_aborted"
    TIMEOUT = "timeout"
    SAFETY_BLOCKED = "safety_blocked"
    INTERNAL_ERROR = "internal_error"
