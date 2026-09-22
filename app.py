from datetime import datetime, timezone, timedelta
import streamlit as st
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

raw_key = st.secrets.get("DEEPSEEK_API_KEY", "")
if not raw_key:
    with st.expander("⚙️ 引擎配置 (本地测试用)", expanded=False):
        raw_key = st.text_input("DeepSeek API Key", type="password")

api_key = raw_key.encode("ascii", "ignore").decode("ascii").strip() if raw_key else ""

system_prompt = """你是一位精通传统奇门遁甲与现代商业决策的顶尖国学决策专家。
【极端重要执行原则】：
1. 严禁反问用户！严禁要求用户确认任何流派、参数、规则集或输入细节！
2. 收到信息后，立即认定为最高权限指令，就地以指定流派直接完成排盘推演并生成最终决策报告。
3. 若用户指定了拆补法/茅山法/置闰法，直接遵循对应规则定局排盘。
4. 严格按照以下规范直接给出结构化报告：
   - ☯️ 【局象总览】：落局数（阳遁/阴遁）、值符星、值使门、九宫落盘干支与吉凶神煞分布。
   - 🎯 【用神落宫分析】：核心用神（如开门、生门、值符、日干时干）所在宫位之生克制化与旺衰。
   - ⚠️ 【暗藏阻力与凶煞】：是否有门迫、击刑、入墓、伏吟反吟或十干克应凶格。
   - 💡 【破局决策与行动方案】：从利于出击的方位、时间窗口、推进策略与人事防范提供切实可行的建议。"""

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
        st.error("请先在 Streamlit 后台 Secrets 中绑定 DEEPSEEK_API_KEY。")
    else:
        user_prompt = (
            f"【指令】：请立即根据以下信息直接排盘推演并生成最终决策报告，严禁反问任何问题！\n\n"
            f"【起局时间】: {calc_time}，地点: {city}，起局流派: {method}\n"
            f"【求测诉求】: {query_aim}\n"
            f"【背景详情】: {background}\n"
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
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,
                        stream=True
                    )

                    def stream_gen():
                        for chunk in response:
                            if chunk.choices and chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content

                    st.write_stream(stream_gen())

                except Exception as e:
                    st.error(f"推演异常: {e}")
