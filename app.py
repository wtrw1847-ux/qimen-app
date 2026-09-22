from datetime import datetime, timezone, timedelta
import streamlit as st
import os
from openai import OpenAI

# 页面基础配置
st.set_page_config(
    page_title="天机·奇门决策系统",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 注入高阶黑金新中式 CSS 样式
st.markdown("""

""", unsafe_allow_html=True)

# 渲染顶部标题
st.markdown("""
天机 · 奇门遁甲决策系统

天地运行 · 凡出九宫 · 格局吉凶 · 决策胜算

""", unsafe_allow_html=True)

安全获取 API Key
api_key = st.secrets.get("DEEPSEEK_API_KEY", None)
if not api_key:
with st.expander("⚙️ 引擎配置 (本地测试用)", expanded=False):
api_key = st.text_input("DeepSeek API Key", type="password")

奇门遁甲规则库
def load_qimen_rules():
skill_file = os.path.join(os.path.dirname(file), "qimen-dunjia", "SKILL.md")
if os.path.exists(skill_file):
with open(skill_file, "r", encoding="utf-8") as f:
return f.read()
return """
你是一位精通正统奇门遁甲排盘、象意解析与现代商业决策推演的高阶国学决策智囊。
请严密依照传统奇门遁甲的九宫八卦、三奇六仪、八门、九星、八神逻辑体系进行推演，并结合用户的求测诉求输出深度决策报告。

【排盘分析核心准则】：

排盘与定局：根据求测时间确定阴阳遁局数，明确值符、值使落宫，排布天盘九星、地盘三奇六仪、人盘八门及神盘八神。

用神辨析：

商业投资/求财：以生门为利润，戊为资本，甲子戊落宫生克关系为核心。

事业/合作：以开门为文职/企业，休门为休整/贵人，日干代表求测者自身，时干代表所求测之事体。

盘面格局审查：

重点审查门迫、击刑、入墓、反吟、伏吟与十干克应吉凶格局（如青龙返首、飞鸟跌穴、白虎猖狂、螣蛇夭矫等）。

决策报告结构要求：

一、排盘概览（九宫落局用神总论）

二、现状与宏观运势（日干时干落宫状态、气数旺衰）

三、潜在阻力与暗藏风险（击刑入墓、门迫凶煞剖析）

四、破局策略与行动路径（利于出击的方向、时间节点与风水/人事趋避方案）
"""

输入表单组件
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

触发推演逻辑
if st.button("启动奇门推演", use_container_width=True):
if not api_key:
st.error("服务尚未绑定秘钥，请在上方引擎配置或云端 Secrets 中填入 DEEPSEEK_API_KEY。")
else:
qimen_rules = load_qimen_rules()
user_prompt = (
f"【起局时间】: {calc_time}，地点: {city}，起局方法: {method} \n"
f"【求测诉求】: {query_aim} \n"
f"【背景详情】: {background} \n"
f"【输出要求】: 严格依据系统设定的规则做出盘面，明确指出本局用神与八门落宫，涵盖现趋势、潜在阻力、可行策略三方面提供详尽建议。"
)

    st.markdown('
', unsafe_allow_html=True)
st.markdown("#### 📜 奇门推演决策报告")
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

    st.markdown('
