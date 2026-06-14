# test_v3_budget_pipeline.py
import logging
from context_models import ChunkEntityV3, SectionContext
from budget_context_builder import BudgetContextBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

if __name__ == "__main__":
    # 1. 离线端沉淀：模拟一个高价值的 Section 元数据实体
    mysql_section = SectionContext(
        id="doc_001-sec_002",
        title="2. 生产环境安装MySQL步骤",
        summary="讲解通过官方规范化的 RPM 存储库进行静默安装、拉起服务并捞取初始临时密码的标准化工业流程。"
    )

    # 2. 模拟从检索和 Rerank 扔出来的 5 个带有自我压缩特征的叶子 Chunks
    mock_chunks = [
        ChunkEntityV3(
            id="C1", section_id=mysql_section.id, order_index=0, score=0.98,
            full_text="[Step 1] 首先需要使用 wget 工具下载官方提供的规范化 rpm 源包。运行命令: wget https://dev.mysql.com/get/mysql80.rpm 并使用 rpm -ivh 进行源的本地固化安装。",
            short_summary="下载并安装官方 RPM 规范源包"
        ),
        ChunkEntityV3(
            id="C2", section_id=mysql_section.id, order_index=1, score=0.95,
            full_text="[Step 2] 源固化完成后，执行企业级静默安装指令: sudo yum install mysql-community-server -y。注意此步骤需要保证外部网络畅通，整个安装包大小约为 550MB。",
            short_summary="执行 yum 静默安装 community-server"
        ),
        ChunkEntityV3(
            id="C3", section_id=mysql_section.id, order_index=2, score=0.91,
            full_text="[Step 3] 安装成功后，使用 systemctl start mysqld 命令唤醒底层的守护进程。并通过 systemctl enable 命令将其牢牢注入到操作系统的开机自启常驻服务队列中。",
            short_summary="拉起守护进程并注入开机自启"
        ),
        ChunkEntityV3(
            id="C4", section_id=mysql_section.id, order_index=3, score=0.62,
            full_text="[Step 4] 首次拉起后，MySQL 会在 /var/log/mysqld.log 中生成一个高度机密的初始随机密码。架构师必须使用 grep 'temporary password' 指令将其捞取出来才能进行首次登录。",
            short_summary="捞取初始临时密码完成首次登录"
        ),
        ChunkEntityV3(
            id="C5", section_id=mysql_section.id, order_index=4, score=0.35,
            full_text="[💡 附录注意事项] 在极少数古老的 CentOS 7.6 机器上，可能会遭遇 mariadb-libs 依赖包冲突的问题，如果撞墙，需要先执行 yum remove mariadb-libs 再行安装。",
            short_summary="处理旧系统 mariadb 依赖冲突"
        )
    ]

    # 3. 初始化架构师的完全体 Context Builder（卡死硬预算：只给 500 字符限制）
    # 这 5 个块的总长度高达 1000 字符以上，必然触发激烈的预算置换与压缩！
    builder = BudgetContextBuilder(max_context_budget=550)

    print("="*60 + "\n🔥 极限工况：触发 V3 预算置换与渐进压缩管线\n" + "="*60)
    
    # 模拟 V2 路由过来的 PROCEDURE 意图
    final_prompt_for_llm = builder.build_context(
        query_intent="PROCEDURE",
        target_sections=[mysql_section],
        recalled_chunks=mock_chunks
    )

    print("\n" + "="*60 + "\n🚀 最终输送给 DeepSeek 的高纯度信息熵 Prompt 上下文\n" + "="*60)
    print(final_prompt_for_llm)
