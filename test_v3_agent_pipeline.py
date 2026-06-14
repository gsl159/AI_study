# test_v3_agent_pipeline.py
import logging
from state_machine_agent import EnterpriseDiagnosticAgent

# 打开高精度全局运维监控日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

# 模拟我们通过底层系统抓取到的真实物理大环境工具集（Environment Shims）
MOCK_LINUX_ENV_TOOLS = {
    "check_netstat_3306": "tcp6  0  0 :::3306 :::* LISTEN -", # 模拟显示端口其实完全空闲，没有被任何人抢占
    "check_mysql_error_log": "2026-06-14T15:20:11.123Z [ERROR] [MY-010119] [Server] Aborting after failing to bind /var/lib/mysql/data: Permission denied", # 💡 致命证据：其实是权限被运维实习生搞烂了！
    "check_disk_space": "/dev/sda1  40G  12G  28G  30% /" # 模拟显示磁盘空间稳健得一塌糊涂
}

if __name__ == "__main__":
    print("="*70 + "\n🔥 LEVEL 3 战役爆发：启动可验证状态机 Agent 进行核心故障收敛\n" + "="*70)
    
    # 初始化完全遵从你意志的钢铁状态机 Agent
    agent_brain = EnterpriseDiagnosticAgent(
        api_key="sk-68901eb2d2894926bb24442944c1eb23",
        base_url="https://api.deepseek.com/v1",
        model_name="deepseek-chat"
    )

    # 发射硬核诊断请求
    result_status = agent_brain.execute_diagnostic_loop(
        problem_description="生产环境的一台核心 MySQL 实例在执行重启后，突然无法正常拉起，守护进程不断 crash 报错。",
        mock_environment_tools=MOCK_LINUX_ENV_TOOLS
    )

    print("\n" + "="*70 + "\n🏁 AGENT 战报收官审计控制台看板\n" + "="*70)
    print(f"🏆 最终诊断状态: {result_status}")
    print("\n📜 完整的、可审计的严密推理路径追踪 (Audit Trail):")
    for idx, step in enumerate(agent_brain.diagnostic_history):
        print(f"  [{idx + 1}] {step}")
