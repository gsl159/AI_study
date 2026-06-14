import streamlit as st
from llm import analyze_large_knowledge_text

st.set_page_config(page_title="AI 知识工作台", layout="centered")
st.title("📚 AI 知识工作台 (Level 1 - 强契约版)")
st.caption("基于 Map-Reduce 与双层 Pydantic 契约锁死的长文本智能精炼器")

user_input = st.text_area("请输入或粘贴你今天看到的任何长篇技术文章、博客或聊天记录：", height=200)

if st.button("开始精炼资产", type="primary"):
    if user_input.strip() == "":
        st.warning("请输入内容后再提交。")
    else:
        with st.spinner("系统正在进行物理切片并循环清洗聚合..."):
            # 此时的 result 是一个清清白白的 FinalAggregatedOutput 对象
            result = analyze_large_knowledge_text(user_input)
            
            st.success("长文本资产精炼并聚合成功！")
            
            # ── 核心恢复：改回点号访问，拥有完美的 IDE 类型提示，不再怕写错键名 ──
            st.subheader("💡 核心摘要")
            st.info(result.summary)
            
            st.subheader("🏷️ 分类标签")
            st.write(result.tags)
            
            st.subheader("🏃 可落地待办事项")
            for item in result.action_items:
                st.markdown(f"- `{item}`")
