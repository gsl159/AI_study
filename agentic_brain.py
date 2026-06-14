# agentic_brain.py
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from agent_models import AgentState, Hypothesis, ExecutionPlan
from tool_registry import EnterpriseToolRegistry

logger = logging.getLogger("RAG-Agent-Brain")

class AgenticKnowledgeSystem:
    def __init__(self, api_key: str, base_url: str, model_name: str, tool_registry: EnterpriseToolRegistry):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model_name
        self.registry = tool_registry
        self.current_state = AgentState.INIT
        self.plan: Optional[ExecutionPlan] = None
        self.runtime_evidence_pool: Dict[str, Any] = {}
        self.audit_trail: List[str] = []

    def _call_llm_json(self, system_prompt: str, user_prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())

    def evaluate_evidence_sufficiency(self) -> float:
        required_indicators = ["service_status", "error_log", "port_status"]
        collected_count = sum(1 for indicator in required_indicators if indicator in self.runtime_evidence_pool)
        score = collected_count / len(required_indicators)
        logger.info(f"📊 [Sufficiency Check] 当前现场证据收集完备度得分: {score:.2f} (已攒齐 {collected_count}/{len(required_indicators)} 项关键指标)")
        return score

    def run_diagnose(self, user_incident: str) -> str:
        logger.info(f"🚨 [根因诊断战役启动] 收到报障: '{user_incident}'")
        self.audit_trail.append(f"报障源: {user_incident}")

        while self.current_state not in [AgentState.SUCCESS, AgentState.FAILED]:
            
            if self.current_state == AgentState.INIT:
                logger.info("🩺 [State: INIT] 现场第一法医就位，拒绝空谈文档，立刻实施物理现场摸底...")
                self.runtime_evidence_pool["service_status"] = self.registry.invoke("check_service", "mysqld")
                self.runtime_evidence_pool["port_status"] = self.registry.invoke("check_port", 3306)
                
                sufficiency_score = self.evaluate_evidence_sufficiency()
                if sufficiency_score < 0.7:
                    logger.warning("⚠️ [Evidence Deficit] 现场痕迹遭遇严重破坏或缺失！强制唤醒外挂 RAG 知识库工具进行历史经验空投...")
                    knowledge_package = self.registry.invoke(
                        "hybrid_retrieve_and_budget_build",
                        query="mysql startup permission failure error log denied",
                        intent="PROCEDURE"
                    )
                    self.runtime_evidence_pool["historical_experience_package"] = knowledge_package
                    self.runtime_evidence_pool["error_log"] = "Captured via Knowledge Base Cross-Verification"
                
                self.current_state = AgentState.GENERATE_HYPOTHESIS

            elif self.current_state == AgentState.GENERATE_HYPOTHESIS:
                logger.info("🧠 [State: GENERATE_HYPOTHESIS] 正在融合『现场硬核物理证据』与『历史提纯知识资产』进行科学推理...")
                
                # 🟢 优化点：在 Prompt 里焊死死纪律，把可动用工具列表喂进去，严禁其手写 Linux 原生命令
                available_tools = list(self.registry.get_all_tools_metadata().keys())
                system_prompt = (
                    "你是一个具备严密逻辑的分布式系统根因推导器。\n"
                    "请阅读目前的现场证据池与历史经验包，生成当前最高优先级的 1 个排障假设。\n"
                    f"【铁律约束】你返回的 'target_tool' 字段必须完全属于以下给定的已知工具列表名单中，【绝对禁止自己发明或编写原生的 Bash Shell 命令】：\n"
                    f"已知工具列表: {available_tools}\n\n"
                    "你必须返回以下 JSON 格式，不包含任何多余文字：\n"
                    "{ 'hypothesis': { 'id': 'H1', 'description': '假设具体成因', 'target_tool': '已知工具列表中的名字' } }"
                )
                user_prompt = f"现场证据与历史包: {str(self.runtime_evidence_pool)}"
                
                raw_res = self._call_llm_json(system_prompt, user_prompt)
                self.plan = ExecutionPlan(hypotheses=[Hypothesis(**raw_res['hypothesis'])])
                self.current_state = AgentState.COLLECT_EVIDENCE

            elif self.current_state == AgentState.COLLECT_EVIDENCE:
                current_hyp = self.plan.hypotheses[0]
                logger.info(f"🎯 [State: COLLECT_EVIDENCE] 正在对核心假设发起饱和打击: [{current_hyp.id}] -> {current_hyp.description}")
                
                #  调用工具进行反向验证（哪怕大模型突破了提示词约束，底层的 registry.invoke 拦截路由器也能把它强制掰回来！）
                real_evidence = self.registry.invoke(current_hyp.target_tool)
                
                self.current_state = AgentState.VERIFY_HYPOTHESIS
                logger.info("⚖️ [State: VERIFY_HYPOTHESIS] 启动 Reflection 审判锁，比对物理铁证...")
                
                system_prompt = (
                    "你是一个冷酷的法医复盘器。请比对你的假设和拿到的物理铁证，判断假设是否100%成立。\n"
                    "必须返回 JSON: { 'is_verified': true/false, 'reasoning': '理由' }"
                )
                user_prompt = f"假设: {current_hyp.description} | 拿到的物理铁证: {real_evidence}"
                
                verify_res = self._call_llm_json(system_prompt, user_prompt)
                if verify_res['is_verified']:
                    logger.info(f"🏆 [根因击穿] 审判通过！凶手浮出水面: {verify_res['reasoning']}")
                    self.audit_trail.append(f"确诊真因: {current_hyp.description}. 逻辑依据: {verify_res['reasoning']}")
                    self.current_state = AgentState.SUCCESS
                else:
                    logger.warning("❌ 假设被铁证无情推翻，切入重规划线...")
                    self.current_state = AgentState.FAILED

        return self.current_state.value