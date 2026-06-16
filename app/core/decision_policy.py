from app.core.diagnostic_result import ConfirmationResult
from app.core.convergence_state import ConvergenceState
from app.evidence.states import DiagnosticOutcome

class DecisionPolicy:
    """业务规则制定者：不产生任何 side effect，纯粹的输入输出映射"""
    
    def evaluate(self, confirmation: ConfirmationResult, convergence: ConvergenceState) -> DiagnosticOutcome:
        # 统一的业务判断逻辑
        if confirmation.confirmed:
            return DiagnosticOutcome.ROOT_CAUSE_CONFIRMED
        
        if convergence == ConvergenceState.STOP_ALL_FALSIFIED:
            return DiagnosticOutcome.FAILED_TO_CONFIRM
            
        if convergence == ConvergenceState.STOP_MAX_ITER:
            return DiagnosticOutcome.INSUFFICIENT_EVIDENCE
            
        return DiagnosticOutcome.INSUFFICIENT_EVIDENCE
