# app/chaos/fault_injector.py
from enum import Enum
import time

class FaultType(Enum):
    TIMEOUT = "timeout"
    EMPTY_RESULT = "empty_result"
    EXECUTION_ERROR = "exec_error"
    DIRTY_DATA = "dirty_data"

class FaultInjector:
    def __init__(self, mode: FaultType = None):
        self.mode = mode

    def inject(self, cmd: str):
        if self.mode == FaultType.TIMEOUT:
            time.sleep(35) # 模拟阻塞
        elif self.mode == FaultType.EMPTY_RESULT:
            return ""
        elif self.mode == FaultType.EXECUTION_ERROR:
            raise PermissionError("Physical permission denied")
