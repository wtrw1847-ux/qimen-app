from datetime import datetime, timezone, timedelta
import streamlit as st
import os
from openai import OpenAI

st.set_page_config(
    page_title="天机·奇门决策系统",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🔮 天机 · 奇门遁甲决策系统")
st.caption("天地运行 · 凡出九宫 · 格局吉凶 · 决策胜算")
st.divider()

api_key = st.secrets.get("DEEPSEEK_API_KEY", None)
if not api_key:
    with st.expander("⚙️ 引擎配置 (本地测试用)", expanded=False):
        api_key = st.text_input("DeepSeek API Key", type="password")

def load_qimen_rules():
    skill_file = os.path.join(os.path.dirname(__file__), "qimen-dunjia", "SKILL.md")
    if os.path.exists(skill_file):
        with open(skill_file, "r", encoding="utf-8") as f:
            return f.read()
    return "你是一位精通传统奇门遁甲的决策专家，需严密依据九宫八门干支规律进行深入分析。"

col1, col2 = st.columns(2)
with col1:
    beijing_now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y年%m月%d日 %H:%M")
    calc_time = st.text_input("起局时间 (公历)", value=beijing_now)
    city = st.text_input("求测地点", value="北京")

with col2:
    method = st.selectbox("起局途径", ["拆补法", "茅山法", "置闰法"])
    query_aim = st.text_input("核心求测诉求", value="这笔自动驾驶项目投资合作线索是否与我合局？")

background = st.text_area(
    "事由脉络与背景概述",
    value="当前处于初期接触讨论阶段，希望对比不同方向在当前运势下的阻力、收益空间及契合度。",
    height=90
)

if st.button("启动奇门推演", use_container_width=True):
    if not api_key:
        st.error("服务尚未绑定秘钥，请在上方引擎配置或云端 Secrets 中填入 DEEPSEEK_API_KEY。")
    else:
        qimen_rules = load_qimen_rules()
        user_prompt = (
            f"【起局时间】: {calc_time}，地点: {city}，起局方法: {method}\n"
            f"【求测诉求】: {query_aim}\n"
            f"【背景详情】: {background}\n"
            f"【输出要求】: 严格依据系统设定的规则做出盘面，明确指出本局用神与八门落宫，涵盖现趋势、潜在阻力、可行策略三方面提供详尽建议。"
        )

        with st.container(border=True):
            st.subheader("📜 奇门推演决策报告")
            with st.spinner("起局排盘中，正在调取九宫落局与吉凶神煞……"):
                try:
                    client = OpenAI(
                        api_key=api_key,
                        base_url="https://api.deepseek.com"
                    )
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": qimen_rules},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2,
                        stream=True
                    )

                    def stream_gen():
                        for chunk in response:
                            if chunk.choices and chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content

                    st.write_stream(stream_gen())

                except Exception as e:
                    st.error(f"推演异常: {e}")
