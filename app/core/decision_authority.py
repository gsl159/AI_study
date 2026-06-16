from app.core.convergence_state import ConvergenceState
from app.core.decision_policy import DecisionPolicy
from app.core.diagnostic_result import ConfirmationResult, DiagnosticResult
from app.core.result_factory import DiagnosticResultFactory
from app.core.result_validator import DiagnosticResultValidator


class DecisionAuthority:
    def __init__(self, policy: DecisionPolicy, factory: DiagnosticResultFactory):
        self.policy = policy
        self.factory = factory

    def decide(self, confirmation: ConfirmationResult, convergence: ConvergenceState) -> DiagnosticResult:
        outcome = self.policy.evaluate(confirmation, convergence)
        # 统一的 Factory 出口，保证数据结构严谨
        result = self.factory.create_from_outcome(outcome, ...)
        DiagnosticResultValidator.validate(result)
        return result
