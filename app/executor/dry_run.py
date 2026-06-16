from dataclasses import dataclass
from app.executor.base_executor import VerificationProbe

@dataclass
class DryRunReport:
    probe_id: str
    action: str
    risk: str
    expected_gain: float
    rollback_available: bool
    approved: bool = False # 初始状态为待审批

class DryRunEngine:
    def evaluate(self, probe: VerificationProbe) -> DryRunReport:
        # 模拟生成审批摘要
        return DryRunReport(
            probe_id=probe.probe_id,
            action=probe.cmd,
            risk=probe.action_type.name,
            expected_gain=0.42, # 预估信息增益
            rollback_available=True if probe.rollback_action else False
        )
