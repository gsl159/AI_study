# retrieval_engine.py
from enum import Enum
from typing import List
import logging
from rag_models import ChunkEntity
from storage_engine import EnterpriseKnowledgeStore

logger = logging.getLogger("RAG-Retrieval-Engine")

class RetrievalMode(Enum):
    CHUNK = "chunk"
    SECTION = "section"
    HYBRID = "hybrid"

class EnterpriseRetrievalEngine:
    """
    工业级策略检索引擎
    根据不同的 RetrievalMode 驱动完全不同的多路召回与组装链路
    """
    def __init__(self, store: EnterpriseKnowledgeStore):
        self.store = store

    def _mock_vector_search_section(self, query: str) -> str:
        """模拟向量检索或关键词检索，精准召回目标 Section ID"""
        # 生产环境中这里会替换为：embedding_client.search() 或 BM25
        # 此处模拟当用户搜索部署时，通过关键词秒级索引到 MySQL 部署章节
        if "部署" in query or "安装" in query:
            for sec_id, sec_entity in self.store.section_index.items():
                if "安装MySQL" in sec_entity.title or "部署" in sec_entity.title:
                    return sec_id
        # 默认返回第一个章节
        return list(self.store.section_index.keys())[0]

    def _mock_vector_search_chunk(self, query: str) -> str:
        """模拟叶子级别的微观 Chunk 向量搜索"""
        if "3306" in query or "端口" in query:
            for chk_id, chk_entity in self.store.chunk_index.items():
                if "port=3306" in chk_entity.content:
                    return chk_id
        return list(self.store.chunk_index.keys())[0]

    def retrieve(self, query: str, mode: RetrievalMode) -> List[ChunkEntity]:
        """主入口：遵循架构师战略，多路分流检索"""
        logger.info(f" 🎯 [Retrieval Engine] 启动检索。当前模式: {mode.value} | 目标查询: '{query}'")
        
        if mode == RetrievalMode.SECTION:
            # ── 💡 你的 Procedure 绝杀检索流 ──────────────────────────────────
            # Step 1: 粗筛定位 Section 节点
            target_sec_id = self._mock_vector_search_section(query)
            target_sec = self.store.section_index[target_sec_id]
            logger.info(f"🌲 [Section 召回] 成功锁定核心技术章节: '{target_sec.title}'")
            
            # Step 2: 通过二级索引，O(1) 斩获全部绑定的叶子 ID
            chunk_ids = self.store.section_chunk_index[target_sec_id]
            
            # Step 3: 通过三级索引，快速回填 Chunk 物理实体
            chunks = [self.store.chunk_index[cid] for cid in chunk_ids]
            
            # Step 4: 强一致性防御：绝对防范底层并发或外键污染导致的无序，强制物理时序排序
            chunks.sort(key=lambda x: x.order_index)
            logger.info(f"⛓️ [完整性保障] 顺次拉取该章节全部 {len(chunks)} 个有序切片，无损拼装完成。")
            return chunks
            
        elif mode == RetrievalMode.CHUNK:
            # ── 💡 传统的 Fact 精准定位检索流 ─────────────────────────────────
            target_chk_id = self._mock_vector_search_chunk(query)
            target_chunk = self.store.chunk_index[target_chk_id]
            logger.info(f"📄 [Chunk 召回] 成功锁定微观核心知识单元 ID: {target_chunk.id}")
            return [target_chunk]
            
        elif mode == RetrievalMode.HYBRID:
            # ── 💡 复杂的排障双路混合流 ──────────────────────────────────────
            logger.info("🔀 [Hybrid 召回] 启动排障拓扑双路召回：同步拉取 Section 概要与错误代码微观 Chunk")
            # 简化演示：同时返回 Section 全部块与精准块
            return list(self.store.chunk_index.values())[:3]
            
        return []
