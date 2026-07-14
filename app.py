"""
AI Log Analyzer - Streamlit Chat Interface
Run with: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import LogAnalyzerAgent
from src.config import Config

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Log Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0d0f14 0%, #111520 60%, #0d1117 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1623 0%, #111827 100%);
    border-right: 1px solid rgba(99,179,237,0.1);
}

/* Section label */
.section-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a90b8;
    margin: 1.4rem 0 0.5rem 0;
}

/* Info card */
.info-card {
    background: rgba(99,179,237,0.05);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    font-size: 0.82rem;
    color: #94a3b8;
    line-height: 1.65;
    margin-bottom: 0.4rem;
}

/* Monospace badge */
.mono-badge {
    font-family: 'JetBrains Mono', monospace;
    background: rgba(99,179,237,0.07);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 6px;
    padding: 0.22rem 0.55rem;
    font-size: 0.72rem;
    color: #63b3ed;
    display: block;
    margin-bottom: 0.3rem;
}

/* Status dot */
.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #48bb78;
    margin-right: 6px;
    vertical-align: middle;
    animation: pulse 2.5s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; } 50% { opacity:0.4; }
}

/* Clear button */
.stButton > button {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.28) !important;
    color: #fc8181 !important;
    border-radius: 8px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    background: rgba(239,68,68,0.2) !important;
    transform: translateY(-1px) !important;
}

/* Main header */
.main-header {
    text-align: center;
    padding: 2rem 0 0.5rem;
}
.main-header h1 {
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed 0%, #9f7aea 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
    margin: 0;
}
.main-header p { color: #64748b; font-size: 0.88rem; margin-top: 0.35rem; }

/* Chat bubbles */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg,rgba(99,179,237,0.1),rgba(159,122,234,0.08));
    border: 1px solid rgba(99,179,237,0.18);
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin-bottom: 0.6rem;
    animation: fadeUp 0.25s ease;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin-bottom: 0.6rem;
    animation: fadeUp 0.25s ease;
}
@keyframes fadeUp {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
}

/* Chat input */
[data-testid="stChatInput"] {
    border-radius: 10px !important;
    border: 1px solid rgba(99,179,237,0.22) !important;
    background: rgba(15,22,35,0.95) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(99,179,237,0.55) !important;
    box-shadow: 0 0 0 3px rgba(99,179,237,0.08) !important;
}

/* Markdown */
.stMarkdown p, .stMarkdown li { color: #cbd5e0; line-height:1.7; }
.stMarkdown h3 { color:#e2e8f0; font-size:0.98rem; font-weight:600; }
.stMarkdown code {
    background: rgba(99,179,237,0.1);
    color: #63b3ed;
    border-radius: 4px;
    padding: 0.12rem 0.38rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.84em;
}

/* Welcome */
.welcome-wrap {
    display:flex; flex-direction:column; align-items:center;
    padding: 3.5rem 1rem; text-align:center;
}
.welcome-icon { font-size:3rem; margin-bottom:0.8rem; }
.welcome-title { font-size:1.25rem; font-weight:600; color:#e2e8f0; margin-bottom:0.4rem; }
.welcome-sub { font-size:0.88rem; color:#64748b; max-width:400px; line-height:1.7; }
.tip-grid {
    display:grid; grid-template-columns:1fr 1fr;
    gap:0.6rem; margin-top:1.8rem; max-width:460px; width:100%;
}
.tip-card {
    background:rgba(99,179,237,0.05);
    border:1px solid rgba(99,179,237,0.14);
    border-radius:10px; padding:0.85rem;
    text-align:left;
}
.tip-icon { font-size:1.2rem; margin-bottom:0.3rem; }
.tip-title { font-size:0.8rem; font-weight:600; color:#e2e8f0; }
.tip-desc  { font-size:0.73rem; color:#64748b; margin-top:0.15rem; }

hr { border-color:rgba(99,179,237,0.08) !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(99,179,237,0.2); border-radius:10px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def build_langchain_history(messages: list) -> list:
    """Convert Streamlit message dicts to LangChain message objects."""
    result = []
    for msg in messages:
        if msg["role"] == "user":
            result.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            result.append(AIMessage(content=msg["content"]))
    return result


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agent" not in st.session_state:
        try:
            Config.validate()
            st.session_state.agent = LogAnalyzerAgent()
        except ValueError as e:
            st.error(f"⚠️ Configuration error: {e}")
            st.stop()


# ── Sidebar ────────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;padding-bottom:1rem;
             border-bottom:1px solid rgba(99,179,237,0.12);margin-bottom:1rem">
            <span style="font-size:1.4rem">🔍</span>
            <span style="font-size:1.05rem;font-weight:700;color:#e2e8f0">AI Log Analyzer</span>
        </div>
        """, unsafe_allow_html=True)

        # Status
        n = len(st.session_state.messages)
        st.markdown(f"""
        <div class="info-card">
            <span class="status-dot"></span>
            <strong style="color:#e2e8f0">Agent ready</strong>
            &nbsp;·&nbsp; <span style="color:#4a5568">{n} message{'s' if n!=1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)

        # Example queries
        st.markdown('<div class="section-label">Try asking</div>', unsafe_allow_html=True)
        examples = [
            "What log files are available?",
            "Read the app.log file",
            "What errors occurred?",
            "When did the connection fail?",
            "Summarize the warnings",
        ]
        for ex in examples:
            st.markdown(f"""
            <div class="info-card" style="padding:0.45rem 0.8rem">
                <span style="color:#4a90b8">›</span> {ex}
            </div>
            """, unsafe_allow_html=True)

        # Config
        st.markdown('<div class="section-label">Config</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <span class="mono-badge">model &nbsp;· &nbsp;{Config.GEMINI_MODEL}</span>
        <span class="mono-badge">temp &nbsp;&nbsp;· &nbsp;{Config.TEMPERATURE}</span>
        <span class="mono-badge">logs &nbsp;&nbsp;· &nbsp;{Config.LOG_DIRECTORY}/</span>
        """, unsafe_allow_html=True)

        # Clear
        st.markdown('<div class="section-label">Controls</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("""
        <div style="margin-top:2rem;text-align:center;color:#1e293b;font-size:0.7rem">
            Powered by Gemini
        </div>
        """, unsafe_allow_html=True)


# ── Welcome screen ─────────────────────────────────────────────────────────────
def welcome():
    st.markdown("""
    <div class="welcome-wrap">
        <div class="welcome-icon">🔍</div>
        <div class="welcome-title">Ready to analyze your logs</div>
        <div class="welcome-sub">
            Ask me anything — I'll read files, find errors, trace timelines,
            and give you clear recommendations.
        </div>
        <div class="tip-grid">
            <div class="tip-card">
                <div class="tip-icon">📁</div>
                <div class="tip-title">Read files</div>
                <div class="tip-desc">Analyze any log in the logs directory</div>
            </div>
            <div class="tip-card">
                <div class="tip-icon">🚨</div>
                <div class="tip-title">Find errors</div>
                <div class="tip-desc">Root cause + cascading failure analysis</div>
            </div>
            <div class="tip-card">
                <div class="tip-icon">📈</div>
                <div class="tip-title">Timeline</div>
                <div class="tip-desc">Reconstruct event sequences</div>
            </div>
            <div class="tip-card">
                <div class="tip-icon">💡</div>
                <div class="tip-title">Recommendations</div>
                <div class="tip-desc">Prioritized P1 / P2 / P3 fixes</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    init_state()
    sidebar()

    st.markdown("""
    <div class="main-header">
        <h1>AI Log Analyzer</h1>
        <p>Ask about your logs in plain English</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Chat history or welcome screen
    if not st.session_state.messages:
        welcome()
    else:
        for msg in st.session_state.messages:
            avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask about your logs…"):
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        # Build history (all messages BEFORE the current one)
        prior_messages = st.session_state.messages[:-1]
        chat_history = build_langchain_history(prior_messages)

        # Query agent — Streamlit owns the history, agent is stateless
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing…"):
                response = st.session_state.agent.process_query(
                    user_input=prompt,
                    chat_history=chat_history,
                )
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
