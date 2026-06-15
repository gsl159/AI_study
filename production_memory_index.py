# production_memory_index.py
import logging
import re
import math
import os
import time
import pickle  # 用于索引与大对象的极速二进制固化
from typing import Dict, List, Optional, Set, Tuple
from memory_taxonomy import ProductionCaseMemory, RootCauseTaxonomy

logger = logging.getLogger("Prod-Enterprise-Memory")

class ProductionMemoryIndexBase:
    """
    企业级长期记忆持久化存储引擎（V5.5.0 WAL + Checkpoint 完全体）
    严格执行总架构师 L4.5 工业指令：
    1. STAGE 1-5 漏斗检索面
    2. WAL 预写日志防断电灾难
    3. Checkpoint 快照秒级秒变热恢复
    4. 彻底脱离纯内存 dict 时代
    """
    def __init__(self, data_dir: str = "memory"):
        self.data_dir = data_dir
        # 物理拓扑目录规划
        self.episodic_dir = os.path.join(data_dir, "episodic")
        self.indexes_dir = os.path.join(data_dir, "indexes")
        self.wal_path = os.path.join(data_dir, "memory.wal")
        self._init_storage_layout()

        # 核心内存镜像
        self.case_registry: Dict[str, ProductionCaseMemory] = {}
        self.topology_inverted_index: Dict[str, Dict[str, List[str]]] = {}
        self.global_token_counts: Dict[str, int] = {}
        self.total_documents = 0

        # 状态控制计数器
        self.commit_counter = 0
        self.checkpoint_interval = 100  # 每 100 次提交强制生成一次物理快照

        # 🚀 启动自适应热恢复流
        self.bootstrap_recovery()

    def _init_storage_layout(self):
        """物理规划企业级目录结构"""
        for path in [self.episodic_dir, self.indexes_dir]:
            if not os.path.exists(path):
                os.makedirs(path)

    # ==========================================
    # 💾 CORE PERSISTENCE LAYER (L4.5 核心实现)
    # ==========================================
    
    def _write_wal(self, case: ProductionCaseMemory):
        """【第四阶段：WAL 预写日志】刚性追加，断电零丢失的钢铁防线"""
        # 利用 pickle 将模型高密度流化，写入持久化追随文件
        with open(self.wal_path, "ab") as wal_file:
            pickle.dump(case, wal_file)

    def _clear_wal(self):
        """快照成功后，安全裁切 WAL，释放磁盘 I/O 压力"""
        if os.path.exists(self.wal_path):
            os.remove(self.wal_path)

    def create_memory_snapshot(self):
        """【第三阶段：Memory Snapshot】类似 Redis / DB Checkpoint 的内存状态全量固化"""
        start_time = time.time()
        logger.info("📸 [Checkpoint] 收到自适应触发指令，正在全量固化内存镜像资产...")
        
        # 1. 固化物理案例空间
        for cid, case in self.case_registry.items():
            case_path = os.path.join(self.episodic_dir, f"{cid}.bin")
            with open(case_path, "wb") as f:
                pickle.dump(case, f)
                
        # 2. 固化索引资产 (将动态编织的 O(1) 倒排网与全局 IDF 基质联合打包)
        index_snapshot = {
            "topology_inverted_index": self.topology_inverted_index,
            "global_token_counts": self.global_token_counts,
            "total_documents": self.total_documents
        }
        index_path = os.path.join(self.indexes_dir, "master_metadata.idx")
        with open(index_path, "wb") as f:
            pickle.dump(index_snapshot, f)

        # 3. 快照落盘成功，安全清空预写日志
        self._clear_wal()
        logger.info(f"💾 [Checkpoint Success] 资产安全入库！耗时: {(time.time() - start_time)*1000:.2f} 毫秒。WAL 已重置。")

    def bootstrap_recovery(self):
        """【第一&二阶段：热恢复流】启动时自适应秒级加载，绝不重复扫描原始大文件"""
        start_time = time.time()
        logger.info("🔄 [Bootstrap] 智能体获得生命，启动企业级长期记忆热恢复协议...")

        index_path = os.path.join(self.indexes_dir, "master_metadata.idx")
        
        # 1. 优先尝试从 Master 索引快照恢复 (P1 标准：10万案例 < 5秒)
        if os.path.exists(index_path):
            logger.info("⚡ [Bootstrap] 发现历史索引快照，启动二进制极速流反序列化...")
            with open(index_path, "rb") as f:
                meta = pickle.load(f)
                self.topology_inverted_index = meta["topology_inverted_index"]
                self.global_token_counts = meta["global_token_counts"]
                self.total_documents = meta["total_documents"]
            
            # 异步恢复物理案例库镜像
            for file_name in os.listdir(self.episodic_dir):
                if file_name.endswith(".bin"):
                    cid = file_name.replace(".bin", "")
                    with open(os.path.join(self.episodic_dir, file_name), "rb") as f:
                        self.case_registry[cid] = pickle.load(f)
            logger.info(f"🚀 [Bootstrap] 快照恢复完毕，已成功载入 {len(self.case_registry)} 项经验资产。")
        else:
            logger.warning("⚠️ [Bootstrap] 未发现索引快照，判定为新集群首次冷启动。")

        # 2. 🚨 终极灾备追溯：强行重放 WAL（预写日志），收拢服务器意外断电砸出来的残余资产
        if os.path.exists(self.wal_path):
            logger.warning("🛡️ [WAL Recovery] 检测到断电留下的残余预写日志！启动重放（Replay）恢复...")
            wal_records = 0
            with open(self.wal_path, "rb") as f:
                while True:
                    try:
                        case = pickle.load(f)
                        # 重新编织进内存控制面（无需重新扫描大盘，原地原装恢复）
                        self.case_registry[case.case_id] = case
                        self._reconstruct_index_in_memory(case)
                        wal_records += 1
                    except EOFError:
                        break
            logger.info(f"🎉 [WAL Recovery Success] 强行抢救回 {wal_records} 条未生成快照的突发断电资产！")

        logger.info(f"🏁 [Bootstrap System Ready] 核心中枢恢复总耗时: {(time.time() - start_time):.4f} 秒！")

    def _reconstruct_index_in_memory(self, case: ProductionCaseMemory):
        """为 WAL 重放专门定制的内存编织器"""
        topo_key = self._get_topology_key(case.raw_fingerprint_data)
        tokens = self._tokenize_log(case.raw_fingerprint_data.get("error_log", ""))
        case.simhash_fingerprint = self._generate_simhash(tokens)
        
        if topo_key not in self.topology_inverted_index:
            self.topology_inverted_index[topo_key] = {}
            
        self.total_documents += 1
        for token in tokens:
            self.global_token_counts[token] = self.global_token_counts.get(token, 0) + 1
            bucket = self.topology_inverted_index[topo_key]
            if token not in bucket:
                bucket[token] = []
            if case.case_id not in bucket[token]:
                bucket[token].append(case.case_id)

    # ==========================================
    # 🚀 ORIGINAL HIGH-PERFORMANCE SEARCH FUNNEL
    # ==========================================
    
    def _get_topology_key(self, features: Dict[str, str]) -> str:
        svc = features.get("service_status", "unknown").lower()
        svc_norm = "failed" if any(x in svc for x in ["fail", "inactive", "exited", "stop"]) else "active"
        port_norm = "free" if "free" in features.get("port_status", "").lower() else "occupied"
        return f"svc:{svc_norm}|port:{port_norm}"

    def _tokenize_log(self, log_text: str) -> Set[str]:
        if not log_text: return set()
        words = re.findall(r'[a-zA-Z0-9_]+', log_text.lower())
        return {w for w in words if len(w) > 1}

    def _generate_simhash(self, tokens: Set[str]) -> str:
        if not tokens: return "0" * 64
        v_bucket = [0] * 64
        for token in tokens:
            token_hash = 14695981039346656037
            for char in token:
                token_hash = token_hash ^ ord(char)
                token_hash = (token_hash * 1099511628211) & 0xFFFFFFFFFFFFFFFF
            for i in range(64):
                bit = (token_hash >> i) & 1
                v_bucket[i] += 1 if bit else -1
        return "".join(["1" if x > 0 else "0" for x in v_bucket])

    def _hamming_distance(self, hash1: str, hash2: str) -> int:
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    def commit_production_case(self, case: ProductionCaseMemory):
        """📥 企业级双写提交：先走 WAL，再写内存，自适应触发快照"""
        # 1. 🛡️ 【第四阶段：WAL】数据未动，预写日志先落地，死守 P3 级断电不丢数据
        self._write_wal(case)
        
        # 2. 编织进入内存高速控制面
        self.case_registry[case.case_id] = case
        topo_key = self._get_topology_key(case.raw_fingerprint_data)
        log_text = case.raw_fingerprint_data.get("error_log", "")
        tokens = self._tokenize_log(log_text)
        case.simhash_fingerprint = self._generate_simhash(tokens)
        
        if topo_key not in self.topology_inverted_index:
            self.topology_inverted_index[topo_key] = {}
            
        self.total_documents += 1
        for token in tokens:
            self.global_token_counts[token] = self.global_token_counts.get(token, 0) + 1
            bucket = self.topology_inverted_index[topo_key]
            if token not in bucket:
                bucket[token] = []
            bucket[token].append(case.case_id)
            
        # 3. 📸 【第三阶段：Checkpoint 快照】自适应周期性收拢
        self.commit_counter += 1
        if self.commit_counter % self.checkpoint_interval == 0:
            self.create_memory_snapshot()

    def fast_path_lsh_recall(self, current_raw_features: Dict[str, str], threshold: Optional[float] = None) -> Optional[ProductionCaseMemory]:
        """🚀 保持 O(1) 吞吐效率的五阶段自适应断路拦截器 (严格捍卫 P2 级性能指标)"""
        topo_key = self._get_topology_key(current_raw_features)
        token_bucket = self.topology_inverted_index.get(topo_key)
        if not token_bucket: return None

        current_log = current_raw_features.get("error_log", "")
        current_tokens = self._tokenize_log(current_log)
        if not current_tokens: return None

        candidate_ids: Set[str] = set()
        for token in current_tokens:
            if token in token_bucket:
                candidate_ids.update(token_bucket[token])
                
        if not candidate_ids: return None

        current_simhash = self._generate_simhash(current_tokens)
        coarse_passed_candidates: List[ProductionCaseMemory] = []
        
        MAX_HAMMING_DISTANCE = 35 
        for cid in candidate_ids:
            case = self.case_registry[cid]
            distance = self._hamming_distance(current_simhash, case.simhash_fingerprint)
            if distance <= MAX_HAMMING_DISTANCE:
                coarse_passed_candidates.append(case)
                
        if not coarse_passed_candidates: return None

        scored_candidates: List[Tuple[float, ProductionCaseMemory]] = []
        hard_threshold = threshold if threshold is not None else 0.45 

        for case in coarse_passed_candidates:
            history_tokens = self._tokenize_log(case.raw_fingerprint_data.get("error_log", ""))
            intersection = current_tokens.intersection(history_tokens)
            
            total_history_weight = sum(self.dict_idf(t) for t in history_tokens)
            matched_weight = sum(self.dict_idf(t) for t in intersection)
            
            rank_score = matched_weight / total_history_weight if total_history_weight > 0 else 0.0
            scored_candidates.append((rank_score, case))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        best_rank_score, final_winner = scored_candidates[0]

        is_hard_passed = best_rank_score >= hard_threshold
        is_relative_passed = False
        if len(scored_candidates) == 1 and best_rank_score >= 0.30:
            is_relative_passed = True
        elif len(scored_candidates) > 1:
            second_score = scored_candidates[1][0]
            if second_score == 0 or (best_rank_score / second_score) >= 2.0:
                if best_rank_score >= 0.30:
                    is_relative_passed = True

        if final_winner and (is_hard_passed or is_relative_passed):
            return final_winner
        return None

    def dict_idf(self, token: str) -> float:
        count = self.global_token_counts.get(token, 0)
        if count == 0: return 1.0
        return math.log10((self.total_documents + 1) / (count + 0.5))