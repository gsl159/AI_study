from enum import Enum

class ConvergenceState(Enum):
    CONTINUE = "continue"
    STOP_CONFIRMED = "stop_confirmed"      # 确诊停止
    STOP_MAX_ITER = "stop_max_iter"        # 到达上限
    STOP_NO_PROGRESS = "stop_no_progress"  # Delta < min_delta
    STOP_ALL_FALSIFIED = "stop_all_falsified" # 全证伪
    STOP_ABORTED = "stop_aborted"          # 异常强制中断
