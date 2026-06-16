from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

class ActionType(Enum):
    READ_ONLY = 0    # 纯只读 (ls, ps, top)
    LIGHT_DIAG = 1   # 轻量诊断 (netstat, kubectl describe)
    SERVICE_MGMT = 2 # 服务管理 (systemctl restart)
    PERMISSION = 3   # 权限变更 (chmod, chown)
    DATABASE = 4     # 数据库操作 (高危，禁止自动执行)

@dataclass
class VerificationProbe:
    probe_id: str
    target_hypothesis: str
    cmd: str  # 必须改为非 shell=True 的列表或完整解析指令
    action_type: ActionType
    expected_evidence: Dict[str, Any]
    timeout: int = 10
    retry_policy: int = 2
    rollback_action: Optional[str] = None

@dataclass
class ProbeResult:
    stdout: str
    exit_code: int
    tool_confidence: float = 0.95  # 增加工具可信度
    latency_ms: int = 0
