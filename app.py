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
from src.agents.log_analyzer import if_confirm
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

/* Approval banner */
.approval-banner {
    background: linear-gradient(135deg, rgba(251,191,36,0.12), rgba(245,158,11,0.06));
    border: 1px solid rgba(251,191,36,0.35);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0 1rem;
}
.approval-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #fbbf24;
    margin-bottom: 0.3rem;
}
.approval-tool {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #f59e0b;
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.2);
    border-radius: 5px;
    padding: 0.15rem 0.5rem;
    display: inline-block;
}
.approval-hint {
    font-size: 0.78rem;
    color: #78716c;
    margin-top: 0.5rem;
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

/* Step history expander */
.step-row {
    font-size: 0.78rem;
    color: #94a3b8;
    padding: 0.2rem 0;
    font-family: 'JetBrains Mono', monospace;
}
.step-ok   { color: #48bb78; }
.step-fail { color: #fc8181; }
.step-blocked { color: #fbbf24; }

hr { border-color:rgba(99,179,237,0.08) !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(99,179,237,0.2); border-radius:10px; }

/* Confirm / cancel buttons */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(99,179,237,0.1) !important;
    border: 1px solid rgba(99,179,237,0.28) !important;
    color: #63b3ed !important;
}
div[data-testid="stHorizontalBlock"] .stButton:last-child > button {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.28) !important;
    color: #fc8181 !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; }
</style>
""", unsafe_allow_html=True)


# ── Tool labels ────────────────────────────────────────────────────────────────
TOOL_LABELS = {
    "list_log_files":        "Listing log files",
    "read_log_file":         "Reading log file",
    "search_logs":           "Searching logs",
    "reboot_rds_instance":   "Rebooting RDS instance",
    "restart_kubernetes_pod": "Restarting Kubernetes pod",
    "send_slack_notification": "Sending Slack notification",
}


def _summarize_result(tool_name: str, result: str) -> str:
    """One-line preview of a tool result for the progress panel."""
    r = str(result)
    if tool_name == "list_log_files":
        count = r.count(".log")
        return f"found {count} log file{'s' if count != 1 else ''}"
    if tool_name == "read_log_file":
        return "file read"
    if tool_name == "search_logs":
        first_line = r.split("\n")[0]
        return first_line.lower() if "Found" in first_line else "search complete"
    if tool_name == "send_slack_notification":
        return "notification sent"
    if tool_name in ("reboot_rds_instance", "restart_kubernetes_pod"):
        return "initiated"
    return r[:80]


# ── StreamlitProgress ──────────────────────────────────────────────────────────
class StreamlitProgress:
    """
    Live progress callbacks rendered inside a st.status container.

    Each callback updates the status label and writes a step line in real time.
    Steps are also recorded in self.steps so they can be replayed as a
    collapsible expander when scrolling back through the conversation.
    """

    def __init__(self, container):
        self.status = container
        self.tool_count = 0
        self.steps: list[dict] = []

    def on_thinking(self):
        self.status.update(label="Thinking…", state="running")

    def on_reasoning(self, text: str):
        if text:
            self.status.write(f"_{text}_")
            self.steps.append({"label": "Reasoning", "detail": text, "kind": "info"})

    def on_tool_start(self, tool_name: str, tool_args: dict):
        self.tool_count += 1
        label = TOOL_LABELS.get(tool_name, tool_name)
        self.status.update(label=f"{label}…", state="running")

    def on_tool_end(self, tool_name: str, result: str, success: bool = True):
        label = TOOL_LABELS.get(tool_name, tool_name)
        marker = "✓" if success else "✗"
        preview = _summarize_result(tool_name, result)
        self.status.write(f"{marker} **{label}** — {preview}")
        self.steps.append({
            "label": label,
            "detail": f"[{'OK' if success else 'FAIL'}] {preview}",
            "kind": "ok" if success else "fail",
        })

    def on_approval_skipped(self, tool_name: str, tool_args: dict):
        label = TOOL_LABELS.get(tool_name, tool_name)
        self.status.write(f"⚠️ **{label}** — requires your approval")
        self.steps.append({
            "label": label,
            "detail": "[BLOCKED] requires approval",
            "kind": "blocked",
        })

    def error(self, message: str):
        self.status.update(label="Error", state="error", expanded=True)
        self.status.write(f"✗ {message}")
        self.steps.append({"label": "Error", "detail": message, "kind": "fail"})

    def complete(self):
        n = self.tool_count
        if n:
            self.status.update(
                label=f"Done — {n} tool{'s' if n != 1 else ''} used",
                state="complete",
                expanded=False,
            )
        else:
            self.status.update(label="Done", state="complete", expanded=False)


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


def render_step_history(steps: list[dict]):
    """Render a collapsible expander showing tool steps for a past message."""
    if not steps:
        return
    with st.expander(f"🔧 {len(steps)} step{'s' if len(steps) != 1 else ''} used", expanded=False):
        for s in steps:
            kind = s.get("kind", "info")
            icon = {"ok": "✓", "fail": "✗", "blocked": "⚠️"}.get(kind, "·")
            css  = {"ok": "step-ok", "fail": "step-fail", "blocked": "step-blocked"}.get(kind, "")
            st.markdown(
                f'<div class="step-row {css}">{icon} <strong>{s["label"]}</strong>'
                f' &mdash; {s["detail"]}</div>',
                unsafe_allow_html=True,
            )


def active_model_label() -> str:
    p = Config.LLM_PROVIDER
    if p == "github":
        return Config.GITHUB_MODEL
    return Config.GEMINI_MODEL


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_blocked" not in st.session_state:
        st.session_state.pending_blocked = None
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
        pending = st.session_state.pending_blocked is not None
        dot_color = "#fbbf24" if pending else "#48bb78"
        status_text = "Awaiting approval" if pending else "Agent ready"
        st.markdown(f"""
        <div class="info-card">
            <span class="status-dot" style="background:{dot_color}"></span>
            <strong style="color:#e2e8f0">{status_text}</strong>
            &nbsp;·&nbsp; <span style="color:#4a5568">{n} message{'s' if n!=1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)

        # Example queries
        st.markdown('<div class="section-label">Try asking</div>', unsafe_allow_html=True)
        examples = [
            "What log files are available?",
            "Analyze backend logs for errors",
            "Check for database connection issues",
            "Restart the orders pod if it's failing",
            "Send a Slack alert about the incident",
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
        <span class="mono-badge">provider · {Config.LLM_PROVIDER}</span>
        <span class="mono-badge">model &nbsp; · {active_model_label()}</span>
        <span class="mono-badge">temp &nbsp;&nbsp; · {Config.TEMPERATURE}</span>
        <span class="mono-badge">logs &nbsp;&nbsp; · {Config.LOG_DIRECTORY}/</span>
        """, unsafe_allow_html=True)

        # Controls
        st.markdown('<div class="section-label">Controls</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_blocked = None
            st.rerun()

        st.markdown("""
        <div style="margin-top:2rem;text-align:center;color:#1e293b;font-size:0.7rem">
            AI Log Analyzer
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
            send Slack alerts, and execute remediation with your approval.
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
                <div class="tip-icon">🔔</div>
                <div class="tip-title">Slack alerts</div>
                <div class="tip-desc">Auto-notify your team on incidents</div>
            </div>
            <div class="tip-card">
                <div class="tip-icon">⚙️</div>
                <div class="tip-title">Remediate</div>
                <div class="tip-desc">Restart pods / reboot RDS with approval</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Approval banner ────────────────────────────────────────────────────────────
def render_approval_banner():
    """
    Show the pending approval banner + Confirm / Cancel buttons below the chat.
    Returns True if the user just clicked a button (triggers rerun).
    """
    blocked = st.session_state.pending_blocked
    if not blocked:
        return

    tool_name = blocked["tool_call"].get("name", "unknown")
    label = TOOL_LABELS.get(tool_name, tool_name)
    tool_args = blocked["tool_call"].get("args", {})

    st.markdown(f"""
    <div class="approval-banner">
        <div class="approval-title">⚠️ Action requires your approval</div>
        <span class="approval-tool">{label}</span>
        <div class="approval-hint">
            Arguments: <code>{tool_args}</code><br>
            Click <strong>Confirm</strong> to execute or <strong>Cancel</strong> to abort.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_confirm, col_cancel, _ = st.columns([1, 1, 4])
    with col_confirm:
        if st.button("✅ Confirm", key="btn_confirm", use_container_width=True):
            _handle_approval(confirmed=True)
    with col_cancel:
        if st.button("❌ Cancel", key="btn_cancel", use_container_width=True):
            _handle_approval(confirmed=False)


def _handle_approval(confirmed: bool):
    """Execute or cancel the pending blocked tool, then rerun."""
    blocked = st.session_state.pending_blocked
    tool_name = blocked["tool_call"].get("name", "unknown")
    label = TOOL_LABELS.get(tool_name, tool_name)

    if confirmed:
        chat_history = build_langchain_history(st.session_state.messages)

        with st.chat_message("assistant", avatar="🤖"):
            with st.status(f"Executing {label}…", expanded=True) as status_box:
                progress = StreamlitProgress(status_box)
                progress.on_thinking()

                result = st.session_state.agent.process_query(
                    user_input="yes",
                    chat_history=chat_history,
                    approval_granted=True,
                )
                progress.complete()

            response = result if isinstance(result, str) else str(result)
            st.markdown(response)

        st.session_state.messages.append({
            "role": "user",
            "content": "yes",
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "steps": progress.steps,
        })
    else:
        response = f"Understood — **{label}** was **not** executed."
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)
        st.session_state.messages.append({"role": "user", "content": "no"})
        st.session_state.messages.append({"role": "assistant", "content": response, "steps": []})

    st.session_state.pending_blocked = None
    st.rerun()


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
    st.info("**Try:** *Analyze backend pod logs and detect issues*")

    # ── Replay conversation history ────────────────────────────────────────────
    if not st.session_state.messages and st.session_state.pending_blocked is None:
        welcome()
    else:
        for msg in st.session_state.messages:
            avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                # Render step expander for assistant messages that recorded steps
                if msg["role"] == "assistant" and msg.get("steps"):
                    render_step_history(msg["steps"])

    # ── Approval banner (shown when a blocked action is pending) ───────────────
    render_approval_banner()

    # ── Chat input ─────────────────────────────────────────────────────────────
    # Disable the input while waiting for an approval decision
    input_disabled = st.session_state.pending_blocked is not None
    input_placeholder = (
        "⚠️ Confirm or cancel the action above before sending a new message…"
        if input_disabled else
        "Ask about your logs…"
    )

    if prompt := st.chat_input(input_placeholder, disabled=input_disabled):
        # Show user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        # Build history (all messages before this one)
        prior_messages = st.session_state.messages[:-1]
        chat_history = build_langchain_history(prior_messages)

        # ── Query agent with live progress ─────────────────────────────────────
        with st.chat_message("assistant", avatar="🤖"):
            with st.status("Analyzing…", expanded=True) as status_box:
                progress = StreamlitProgress(status_box)
                progress.on_thinking()

                try:
                    result = st.session_state.agent.process_query(
                        user_input=prompt,
                        chat_history=chat_history,
                    )
                except Exception as e:
                    progress.error(str(e))
                    result = f"Error: {e}"

                # ── Blocked sentinel → store and surface approval banner ────────
                if isinstance(result, dict) and result.get("blocked"):
                    st.session_state.pending_blocked = result
                    tool_name = result["tool_call"].get("name", "unknown")
                    progress.on_approval_skipped(tool_name, result["tool_call"].get("args", {}))
                    progress.complete()

                    response = result["message"]
                    st.markdown(response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "steps": progress.steps,
                    })
                    st.rerun()

                # ── Normal response ────────────────────────────────────────────
                else:
                    progress.complete()
                    response = result if isinstance(result, str) else str(result)
                    st.markdown(response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "steps": progress.steps,
                    })


if __name__ == "__main__":
    main()
