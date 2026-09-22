from datetime import datetime, timezone, timedelta
import streamlit as st
import os
from google import genai

# 页面基础配置
st.set_page_config(
    page_title="天机·奇门决策系统",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 注入高阶黑金新中式 CSS 样式
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    .header-container {
        text-align: center;
        padding: 2.2rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.25);
        margin-bottom: 2rem;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        background: linear-gradient(135deg, #fce0ad 0%, #dfac6c 50%, #c68b45 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        letter-spacing: 0.08em;
    }
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #161e2e !important;
        border: 1px solid #2d3748 !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.25) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #d4af37 0%, #aa7c11 100%) !important;
        color: #0b0f19 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 2rem !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5) !important;
        color: #000000 !important;
    }
    .report-card {
        background-color: #131b2e;
        border-left: 3px solid #d4af37;
        border-radius: 0 8px 8px 0;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# 顶部沉浸式标题栏
st.markdown("""
<div class="header-container">
    <div class="header-title">天机 · 奇门遁甲决策系统</div>
    <div class="header-subtitle">天道运行 · 八卦九宫 · 格局吉凶 · 决策推演</div>
</div>
""", unsafe_allow_html=True)

# 安全获取 API Key（优先读取 Streamlit 云端 Secrets，本地测试提供折叠输入备用）
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    with st.expander("⚙️ 引擎配置 (本地测试用)", expanded=False):
        api_key = st.text_input("Gemini API Key", type="password")

# 读取本地知识库 SKILL.md
def load_qimen_rules():
    skill_file = os.path.join(os.path.dirname(__file__), "qimen-dunjia", "SKILL.md")
    if os.path.exists(skill_file):
        with open(skill_file, "r", encoding="utf-8") as f:
            return f.read()
    return "你是一位精通传统奇门遁甲的决策专家，需严密依据九宫八门干支规律进行深入分析。"

# 输入表单组件
col1, col2 = st.columns(2)
with col1:
    beijing_now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y年%m月%d日 %H:%M")
    calc_time = st.text_input("起局时间 (公历)", value=beijing_now)
    city = st.text_input("求测地域", value="北京")
with col2:
    method = st.selectbox("排盘流派", ["拆补法", "置闰法", "茅山法"])
    query_aim = st.text_input("核心研判诉求", value="近期启动新项目的合作推进前景与收益抉择")

background = st.text_area(
    "事由脉络与背景描述",
    value="当前处于前期论证阶段，希望对比不同方向在当前运势下的阻力、收益空间及契合度。",
    height=90
)

# 触发推演逻辑
if st.button("启动奇门推演", use_container_width=True):
    if not api_key:
        st.error("服务尚未绑定秘钥，请在上方引擎配置或云端 Secrets 中填入 GEMINI_API_KEY。")
    else:
        qimen_rules = load_qimen_rules()
        user_prompt = (
            f"起局时间：{calc_time}，地域：{city}，定局方法：{method}。\n"
            f"研判诉求：{query_aim}。\n"
            f"背景详情：{background}。\n"
            f"输出要求：严格依据系统设定规则排定盘面，明确定位体用用神与八门格局，从客观趋势、潜在阻力、可行策略三方面提供详尽断语。"
        )

        st.markdown('<div class="report-card">', unsafe_allow_html=True)
        st.markdown("#### 📜 奇门推演决疑报告")
        with st.spinner("起局排盘中，正在调取九宫落局与吉凶神煞..."):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content_stream(
                    model="gemini-3.8-flash",
                    contents=user_prompt,
                    config={
                        "system_instruction": qimen_rules,
                        "temperature": 0.2
                    }
                )
                st.write_stream(chunk.text for chunk in response if chunk.text)
            except Exception as e:
                st.error(f"推演异常：{e}")
        st.markdown('</div>', unsafe_allow_html=True)
