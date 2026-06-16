# app/core/result_validator.py
class InvalidDiagnosticResult(Exception): pass

class DiagnosticResultValidator:
    @staticmethod
    def validate(res: DiagnosticResult):
        if not (0.0 <= res.confidence <= 1.0):
            raise InvalidDiagnosticResult(f"Invalid confidence: {res.confidence}")
        if res.verified_evidence_count < 0:
            raise InvalidDiagnosticResult("Negative evidence count")
        if not (0.0 <= res.conflict_ratio <= 1.0):
            raise InvalidDiagnosticResult("Invalid conflict ratio")
