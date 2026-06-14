# test_router.py
import logging
from router_service import EnterpriseQueryRouter

# 强制打开日志显示
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

if __name__ == "__main__":
    # 初始化你的完全体企业级路由器
    router = EnterpriseQueryRouter(
        api_key="sk-68901eb2d2894926bb24442944c1eb23",
        base_url="https://api.deepseek.com/v1",
        model_name="deepseek-chat"
    )

    print("\n" + "="*50 + "\n🔥 场景 1：规则路由器（Rule Router）直接截获\n" + "="*50)
    res1 = router.route("如何部署MySQL集群？")
    print(f"📊 最终输出结果 -> 意图: {res1.intent} | 置信度: {res1.confidence}")

    print("\n" + "="*50 + "\n🔥 场景 2：规则未命中，大模型处理复杂语义\n" + "="*50)
    # 这句话没有触发任何“怎么、如何、失败”等硬编码词，必须靠 LLM 理解语义
    res2 = router.route("解释一下向量数据库里的余弦相似度跟内积的区别和应用场景")
    print(f"📊 最终输出结果 -> 意图: {res2.intent} | 置信度: {res2.confidence}")

    print("\n" + "="*50 + "\n🚨 场景 3：网络断开、或模型调皮返回错误 JSON 触发 Fallback 安全气囊\n" + "="*50)
    # 注入一个错误的配置，或者断开网络来模拟崩溃
    broken_router = EnterpriseQueryRouter(api_key="sk-wrong-key", base_url="https://api.deepseek.com/v1", model_name="deepseek-chat")
    res3 = broken_router.route("MySQL突然崩了，Error code 137 怎么搞？")
    print(f"📊 最终输出结果 -> 意图: {res3.intent} | 置信度: {res3.confidence} (系统未崩溃，成功返回兜底)")
