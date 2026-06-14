# tool_registry.py
import logging
import time
from typing import Callable, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("RAG-Monitor-Registry")

class ToolEntity(BaseModel):
    name: str
    description: str
    func: Callable[..., Any]

class EnterpriseToolRegistry:
    """
    企业级工具中央调度控制面（V3.2 完备体）
    具备 AOP 拦截器监控、模糊语义路由以及工具元数据导出能力
    """
    def __init__(self):
        self._registry: Dict[str, ToolEntity] = {}
        self.metrics_monitor: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, func: Callable[..., Any]):
        self._registry[name] = ToolEntity(name=name, description=description, func=func)
        self.metrics_monitor[name] = {"call_count": 0, "total_latency_ms": 0.0, "status_history": []}
        logger.info(f"🛠️  [武器库] 成功装备并开启监控打点: '{name}'")

    def get_all_tools_metadata(self) -> Dict[str, str]:
        """
        🟢 补回丢失的契约方法：导出当前武器库中所有注册工具的元数据
        供 Agent 的 Planner 动态感知并生成合规的执行计划
        """
        return {name: tool.description for name, tool in self._registry.items()}

    def _resolve_tool_name(self, raw_name: str) -> str:
        """
        🛡️ 工具名对齐路由器（Tool Name Resolver）
        消灭大模型脑补真实 Bash 命令的幻觉，强制映射回注册表安全沙盒工具中。
        """
        if raw_name in self._registry:
            return raw_name
            
        logger.warning(f"⚠️ [幻觉拦截] 检测到大模型脑补了未注册的工具/命令: '{raw_name}'，启动语义安全路由...")
        
        normalized = raw_name.lower()
        # 规则1：如果脑补的命令里包含了查看 /var/lib/mysql 权限的影子，路由到权限验证桩
        if "ls" in normalized and "mysql" in normalized:
            logger.info("🎯 [路由命中] 成功将脑补 Bash 命令安全重定向至系统备案工具 -> 'verify_mysql_dir_permission'")
            return "verify_mysql_dir_permission"
            
        # 规则2：如果包含了检查服务状态
        if "systemctl" in normalized or "service" in normalized:
            return "check_service"
            
        # 兜底机制
        raise ValueError(f"❌ 恶意或未知的工具调用被安全断路器拦截: '{raw_name}'")

    def invoke(self, name: str, *args, **kwargs) -> Any:
        # 穿过对齐守门人
        resolved_name = self._resolve_tool_name(name)
        
        self.metrics_monitor[resolved_name]["call_count"] += 1
        start_time = time.perf_counter()
        
        logger.info(f"⚙️  [监控拦截] 物理工具 [{resolved_name}] 进入流式调度网... (原请求名: '{name}')")
        
        try:
            result = self._registry[resolved_name].func(*args, **kwargs)
            latency_ms = (time.perf_counter() - start_time) * 1000
            self.metrics_monitor[resolved_name]["total_latency_ms"] += latency_ms
            self.metrics_monitor[resolved_name]["status_history"].append("SUCCESS")
            return result
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self.metrics_monitor[resolved_name]["total_latency_ms"] += latency_ms
            self.metrics_monitor[resolved_name]["status_history"].append(f"FAILED: {type(e).__name__}")
            raise e

    def print_production_dashboard(self):
        print("\n" + "="*25 + " 📊 PROD OBSERVABILITY MONITOR " + "="*25)
        print(f"{'工具名称':<32} | {'调用次数':<8} | {'平均延迟(ms)':<14} | {'近三次运行轨迹'}")
        print("-" * 75)
        for tool_name, data in self.metrics_monitor.items():
            avg_latency = data["total_latency_ms"] / data["call_count"] if data["call_count"] > 0 else 0.0
            history_str = " -> ".join(data["status_history"][-3:]) if data["status_history"] else "NO_CALL"
            print(f"{tool_name:<32} | {data['call_count']:<8} | {avg_latency:<14.2f} | [{history_str}]")
        print("="*75)
