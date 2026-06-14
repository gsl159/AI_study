# test_pipeline.py
from parser_engine import MarkdownSectionParser

# 模拟你企业知识库中一篇硬核的万字操作手册
mock_mysql_guide = """# MySQL 8.0 生产环境部署指南

## 1. 环境准备
操作系统要求：Ubuntu 22.04 LTS 或 CentOS 7.9。
硬件最低配置：4核CPU，8G内存。
执行以下命令关闭防火墙或开放安全组：
sudo systemctl stop ufw

## 2. 安装MySQL
下载并安装官方源：
wget https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm
sudo rpm -ivh mysql80-community-release-el7-3.noarch.rpm
sudo yum install mysql-community-server -y

## 3. 配置my.cnf
编辑配置文件 /etc/my.cnf，注入核心高并发参数：
[mysqld]
port=3306
max_connections=2000
innodb_buffer_pool_size=4G
"""

if __name__ == "__main__":
    # 初始化你的 V1 Ingestion 引擎（设置超小 ChunkSize=50 以便肉眼观察切片效果）
    parser = MarkdownSectionParser(chunk_size=60, overlap=10)
    
    # 物理注入
    doc_entity = parser.parse_to_entity(
        doc_title="MySQL_Deploy_v8.md", 
        raw_markdown=mock_mysql_guide,
        metadata={"author": "DBA_Team", "classification": "Confidential"}
    )
    
    # ── 架构师审计控制台输出 ───────────────────────────────────────────
    print(f"========================================================")
    print(f"📂 成功注入文档: {doc_entity.title} | ID: {doc_entity.id}")
    print(f"🔒 安全级别: {doc_entity.metadata['classification']}")
    print(f"========================================================")
    
    for sec in doc_entity.sections:
        print(f"\n🌲 [Section 枝干节点] 标题: {sec.title} (Level: {sec.level})")
        print(f"   └─ 原始文字总长度: {len(sec.raw_content)} 字符")
        
        for chk in sec.chunks:
            # 缩进打印叶子节点
            print(f"      📄 [Chunk 叶子存储单元] ID: {chk.id} | Index: {chk.chunk_index}")
            print(f"         内容摘要: {repr(chk.content[:40])}...")
