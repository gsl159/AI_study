# router_service.py
import json
import logging
import re
import time
from openai import OpenAI
from router_models import RouterOutput

logger = logging.getLogger("RAG-Router-Monitor")

# 静态资产：定义控制面允许的业务意图集合
ALLOWED_INTENTS = {"FACT_QA", "PROCEDURE", "TROUBLESHOOTING", "COMPARE", "CONFIGURATION"}

class EnterpriseQueryRouter:
    """
    四层立体防御 Query Router
    1. Rule Router -> 2. LLM Router -> 3. Pydantic Validator -> 4. Business Circuit Breaker -> 5. Fallback
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model_name

        # 预编译前置规则，追求微秒级匹配性能
        self.rules = [
            (re.compile(r"(怎么|如何|步骤|怎么做|搭建|部署|配置|安装|构建)"), "PROCEDURE"),
            (re.compile(r"(失败|报错|启动不了|打不开|怎么办|故障|错误|崩溃|Exception|Error|无法启动)"), "TROUBLESHOOTING"),
            (re.compile(r"(区别|不同|对比|优势|劣势|相比于|和.*哪个好)"), "COMPARE"),
            (re.compile(r"(端口|参数|文件路径|大小设置|内核参数)"), "CONFIGURATION")
        ]

    def _rule_route(self, query: str) -> RouterOutput | None:
        """【第一层：Rule Router】零成本、高并发拦截"""
        for regex, intent in self.rules:
            if regex.search(query):
                logger.info(f"⚡ [Rule Router] 规则秒级命中！意图: {intent}")
                return RouterOutput(intent=intent, confidence=1.0)
        return None

    def _llm_route_unsafe(self, query: str) -> RouterOutput:
        """【第二、三层：LLM 驱动 + Pydantic 校验】"""
        system_prompt = (
            "你是一个精密的企业级查询意图分析器。请阅读用户问题，分析其所属的意图类型。\n"
            f"你必须且只能从以下意图列表中选择一个：{list(ALLOWED_INTENTS)}\n"
            "【关键规则】：你必须只返回一个合法的 JSON 对象，绝对禁止包含任何 Markdown 标记或换行。\n"
            "JSON 结构：{ 'intent': '意图大写', 'confidence': 0.95 }"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0, # 锁死随机性
            response_format={"type": "json_object"} # 强开 JSON Mode
        )
        
        raw_content = response.choices[0].message.content.strip()
        data = json.loads(raw_content)
        
        # Pydantic 暴力拦截不合规格式（第一道保险：契约安全）
        parsed_output = RouterOutput.model_validate(data)
        return parsed_output

    def route(self, query: str) -> RouterOutput:
        """主入口：全链路立体防御网"""
        start_time = time.time()
        logger.info(f"🔍 [Router] 收到查询请求: '{query}'")

        try:
            # 1. 前置规则路由
            rule_result = self._rule_route(query)
            if rule_result:
                return rule_result

            # 2. LLM 语义路由与 Pydantic 校验
            logger.info("🧠 [Rule Miss] 规则未命中，正在唤醒大模型进行复杂语义决策...")
            parsed_result = self._llm_route_unsafe(query)

            # 3. 第四层：Python 代码层业务断路器（第二道保险：业务安全）
            if parsed_result.intent not in ALLOWED_INTENTS:
                logger.error(f"❌ [Business Circuit Breaker] 拦截！Pydantic 通过了但业务代码不认可该意图: {parsed_result.intent}")
                # 触发业务异常，直接滑向 fallback
                raise ValueError("Business validation failed")

            duration = time.time() - start_time
            logger.info(f"✅ [Router] 路由决策成功: {parsed_result.intent} | 置信度: {parsed_result.confidence:.2f} | 耗时: {duration:.2f}s")
            return parsed_result

        except Exception as e:
            # 4. 第五层：默认降级策略（Fallback 安全气囊）
            logger.error(f"🚨 [Fallback Activated] 路由平面触发崩溃防护! 原因: {str(e)}。系统自动无感切向最稳健的安全平原: FACT_QA")
            return RouterOutput(intent="FACT_QA", confidence=0.0)
