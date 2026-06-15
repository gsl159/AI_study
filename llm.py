import json
import asyncio
import time
import logging
import hashlib  # 引入加密哈希库
import openai
from models import TextAnalysisOutput, FinalAggregatedOutput
from reducer import aggregate_and_deduplicate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("AI-Systems-Monitor")

DEEPSEEK_API_KEY  = "sk-cea2398a89e3499f8eb6cdca14bbf3ec"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL    = "deepseek-chat"

# ── 💡 你的系统版本资产化：将版本号作为控制变量 ───────────────────────────
PROMPT_VERSION = "v1.2.0"  # 提示词版本
TAG_VERSION    = "v1.0.0"  # 18个核心标签的名单版本

ALLOWED_TAGS = {
    "LLM", "Agent", "RAG", "LangChain", "LangGraph", "MCP", 
    "Prompt工程", "模型部署", "推理优化", "AI工程化", "多模态", 
    "向量数据库", "知识图谱", "数据处理", "论文解读", "框架更新", 
    "最佳实践", "性能优化"
}

# ── 🏭 内存缓存数据库（全局唯一单例） ────────────────────────────────────
GLOBAL_SYSTEM_CACHE = {}

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

async def async_extract_single_chunk(client: openai.AsyncOpenAI, chunk: str, chunk_id: int, semaphore: asyncio.Semaphore) -> TextAnalysisOutput:
    system_prompt = (
        "你是一个严谨的 AI 技术知识整理专家。请阅读用户输入的文字片段，严格按照要求输出 JSON。\n"
        f"允许使用的官方标签列表严格限制为：{list(ALLOWED_TAGS)}\n"
        "【关键规则】：如果文本内容不属于上述官方标签列表中的任何一个领域，"
        "则 tags 字段必须输出为空列表 []，绝对禁止自行发明任何新标签。\n"
        "JSON 结构：{ 'summary': '50字内', 'tags': ['符合的官方标签'], 'action_items': ['动词开头'] }"
    )
    
    async with semaphore:
        start_time = time.time()
        try:
            response = await client.chat.completions.create(
                model=DEEPSEEK_MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": chunk}], temperature=0.1
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
                raw = raw.strip()
            return TextAnalysisOutput(**json.loads(raw))
        except Exception as e:
            return TextAnalysisOutput(summary="当前分片解析失败", tags=[], action_items=[])

# ── 总控运行时：挂载缓存穿透防御 ─────────────────────────────────────────
async def analyze_large_knowledge_text_async(user_text: str) -> FinalAggregatedOutput:
    # 1. ── 💡 完美落地你的复合哈希算法 ──────────────────────────────────
    # 将原文、提示词版本、标签版本拼接组合成唯一的联合输入
    combined_raw_string = f"{user_text.strip()}{PROMPT_VERSION}{TAG_VERSION}"
    cache_key = hashlib.sha256(combined_raw_string.encode("utf-8")).hexdigest()
    # ──────────────────────────────────────────────────────────────────
    
    # 2. 检查缓存是否命中
    if cache_key in GLOBAL_SYSTEM_CACHE:
        logger.info(f"🎯 [Cache Hit] 完美命中本地复合缓存！联合指纹: {cache_key[:16]}...")
        logger.info(f"💰 [零消耗] 本次请求 0延时、0 Token，直接回流内存资产。")
        return GLOBAL_SYSTEM_CACHE[cache_key]
        
    # 3. 缓存未命中（Cache Miss），正常走网络流水线
    logger.info(f"💨 [Cache Miss] 未命中缓存。新联合指纹: {cache_key[:16]}... 正在唤醒 DeepSeek 异步流水线...")
    
    client = openai.AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    chunks = chunk_text(user_text)
    
    global_start_time = time.time()
    sem = asyncio.Semaphore(3)
    tasks = [async_extract_single_chunk(client, chunk, i+1, sem) for i, chunk in enumerate(chunks)]
    chunk_results = await asyncio.gather(*tasks)
    
    final_output = aggregate_and_deduplicate(chunk_results, ALLOWED_TAGS)
    
    # 4. ── 核心写入：将高价值的总报告资产塞进缓存库 ─────────────────────────
    GLOBAL_SYSTEM_CACHE[cache_key] = final_output
    logger.info(f"💾 [Cache Store] 已成功将最终聚合资产固化回内存数据库。")
    
    return final_output