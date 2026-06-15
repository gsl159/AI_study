# simhash_engine.py
import hashlib
from typing import Dict, List

class SimHashEngine:
    """
    工业级轻量文本指纹提纯引擎（64位 SimHash 实现）
    核心优势：文本发生微小噪点变化时，指纹具备局部敏感性（Hamming Distance 线性可度量）
    """
    @staticmethod
    def _fnv1a_64(string: str) -> int:
        """64位高性能 FNV-1a 哈希算法，将单词砸碎为 64位二进制"""
        hash_val = 0xcbf29ce484222325
        for char in string.encode("utf-8", "ignore"):
            hash_val ^= char
            hash_val = (hash_val * 0x00000100000001B3) & 0xffffffffffffffff
        return hash_val

    @classmethod
    def generate_fingerprint(cls, features: Dict[str, str]) -> str:
        """
        将现场物理特征矩阵展平、加权、打碎，融合成一串 64 位的二进制全息特征指纹
        """
        # 展平特征向量，并进行分词分块
        combined_text = []
        for k, v in features.items():
            combined_text.extend(f"{k}:{v}".lower().split())

        # 初始化 64 位特征序列向量桶
        v_bucket = [0] * 64
        
        for word in combined_text:
            if not word: continue
            word_hash = cls._fnv1a_64(word)
            
            # 64位全息投影加权
            for i in range(64):
                bit = (word_hash >> i) & 1
                if bit:
                    v_bucket[i] += 1  # 命中特征，权重正向叠加
                else:
                    v_bucket[i] -= 1  # 未命中，权重负向削减

        # 降维压缩：将 64 位正负桶强行转换为 0 和 1 的刚性指纹
        fingerprint_bits = 0
        for i in range(64):
            if v_bucket[i] > 0:
                fingerprint_bits |= (1 << i)
                
        # 返回 64位二进制补齐字符串
        return f"{fingerprint_bits:064b}"

    @staticmethod
    def calculate_hamming_distance(hash_str1: str, hash_str2: str) -> int:
        """计算两串指纹的海明距离（不同位数的绝对数量）。距离越小，文本相似度越高"""
        return sum(c1 != c2 for c1, c2 in zip(hash_str1, hash_str2))

    @classmethod
    def calculate_similarity(cls, hash_str1: str, hash_str2: str) -> float:
        """将海明距离归一化转换为 0.0 ~ 1.0 的相似度概率"""
        distance = cls.calculate_hamming_distance(hash_str1, hash_str2)
        return (64.0 - distance) / 64.0
