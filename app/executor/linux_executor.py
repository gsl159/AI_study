import subprocess
import shlex
import time
from app.executor.base_executor import VerificationProbe, ProbeResult, ActionType

class LinuxExecutor:
    """
    Level 5.1 工业级执行器：生产环境安全执行
    """
    def execute(self, probe: VerificationProbe) -> ProbeResult:
        # 1. 风险前置评估 (Dry Run 状态机挂载点)
        if probe.action_type in [ActionType.DATABASE]:
             raise PermissionError(f"🚨 [Security] 触发生产熔断：禁止执行 {probe.action_type.name} 类型指令")

        # 2. shlex 安全解析，防止命令注入
        cmd_args = shlex.split(probe.cmd)
        
        start_time = time.perf_counter()
        # 3. 剥离 shell=True，执行子进程
        proc = subprocess.run(
            cmd_args, 
            capture_output=True, 
            text=True, 
            timeout=probe.timeout
        )
        latency = int((time.perf_counter() - start_time) * 1000)
        
        return ProbeResult(
            stdout=proc.stdout,
            exit_code=proc.returncode,
            tool_confidence=0.98 if probe.action_type == ActionType.READ_ONLY else 0.85,
            latency_ms=latency
        )
