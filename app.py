import streamlit as st
import json
import os
import time
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Support Reply Copilot",
    page_icon="⚡",
    layout="wide",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "total_analyzed" not in st.session_state:
    st.session_state.total_analyzed = 0
if "deflected_count" not in st.session_state:
    st.session_state.deflected_count = 0
if "last_elapsed" not in st.session_state:
    st.session_state.last_elapsed = None

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp { background: #0f0f0e; }
h1,h2,h3,h4 { font-family: 'DM Mono', monospace; }

.block-container {
    padding-top: 1.75rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* ── Top bar ── */
.topbar {
    background: #181817;
    border: 1px solid #2a2a28;
    border-radius: 10px;
    padding: 0.9rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
}
.topbar-left {
    display: flex; align-items: center; gap: 10px;
}
.topbar-indicator {
    width: 8px; height: 8px; border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 0 3px rgba(74,222,128,0.15);
}
.topbar-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.95rem; font-weight: 500;
    color: #e8e6e1;
    margin: 0;
}
.topbar-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem; font-weight: 500;
    background: #1f2d1f; color: #4ade80;
    border: 1px solid #2d4a2d;
    padding: 2px 8px; border-radius: 3px;
    letter-spacing: 1.5px; text-transform: uppercase;
}
.topbar-right {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem; color: #555;
}

/* ── Stats ── */
.stats-row {
    display: flex; gap: 0.75rem; margin-bottom: 1.25rem;
}
.stat-card {
    flex: 1;
    background: #181817;
    border: 1px solid #2a2a28;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
}
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem; font-weight: 500;
    color: #555; text-transform: uppercase;
    letter-spacing: 1.2px; margin-bottom: 0.3rem;
}
.stat-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.5rem; font-weight: 500; color: #e8e6e1;
    line-height: 1;
}
.stat-sub {
    font-size: 0.7rem; color: #444; margin-top: 0.2rem;
}

/* ── Panels ── */
.panel {
    background: #181817;
    border: 1px solid #2a2a28;
    border-radius: 10px;
    padding: 1.4rem;
}
.panel-header {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem; font-weight: 500;
    color: #555; text-transform: uppercase;
    letter-spacing: 1.2px; margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #222;
}

/* ── Streamlit form elements ── */
.stTextArea > div > div > textarea {
    background: #111110 !important;
    border: 1px solid #2a2a28 !important;
    border-radius: 8px !important;
    color: #d4d2cc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    resize: vertical !important;
}
.stSelectbox > div > div {
    background: #111110 !important;
    border: 1px solid #2a2a28 !important;
    border-radius: 8px !important;
    color: #d4d2cc !important;
}
.stSelectbox label, .stTextArea label {
    color: #777 !important;
    font-size: 0.78rem !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* ── Button ── */
.stButton > button {
    background: #e8e6e1 !important;
    color: #0f0f0e !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    letter-spacing: 0.5px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #fff !important;
}

/* ── Result sections ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem; font-weight: 500; color: #555;
    text-transform: uppercase; letter-spacing: 1.2px;
    margin-bottom: 0.4rem; margin-top: 1.1rem;
}

/* ── Badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem; font-weight: 500;
    padding: 5px 12px; border-radius: 5px;
}
.badge-green  { background: #1a2e1a; color: #4ade80; border: 1px solid #2d4a2d; }
.badge-yellow { background: #2a2415; color: #fbbf24; border: 1px solid #4a3c1a; }
.badge-red    { background: #2a1515; color: #f87171; border: 1px solid #4a2020; }
.badge-blue   { background: #15202a; color: #60a5fa; border: 1px solid #1a3a5a; }
.badge-gray   { background: #202020; color: #888; border: 1px solid #333; }

/* ── Deflection box ── */
.deflection-box {
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    font-size: 0.85rem;
    line-height: 1.65;
    margin: 0;
}
.deflect    { background: #1a2e1a; border: 1px solid #2d4a2d; color: #86efac; }
.human      { background: #2a1515; border: 1px solid #4a2020; color: #fca5a5; }

/* ── Reply box ── */
.reply-box {
    background: #111110;
    border: 1px solid #2a2a28;
    border-left: 3px solid #4ade80;
    border-radius: 0 8px 8px 0;
    padding: 1.1rem 1.3rem;
    font-size: 0.87rem;
    line-height: 1.8;
    color: #c8c6c0;
    white-space: pre-wrap;
}

/* ── Confidence bar ── */
.conf-track {
    background: #222;
    border-radius: 99px;
    height: 4px;
    width: 100%;
    overflow: hidden;
    margin-top: 5px;
}
.conf-fill { height: 100%; border-radius: 99px; }
.conf-high   { background: #4ade80; }
.conf-medium { background: #fbbf24; }
.conf-low    { background: #f87171; }
.conf-pct {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; color: #555; margin-top: 4px;
}

/* ── Flags ── */
.flag-item {
    display: inline-flex; align-items: center; gap: 5px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    background: #2a1a15; color: #fb923c;
    border: 1px solid #4a2a18;
    padding: 3px 9px; border-radius: 4px;
    margin: 2px 3px 2px 0;
}

/* ── Tags ── */
.tag-item {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    background: #1e1e1c; color: #666;
    border: 1px solid #2a2a28;
    padding: 2px 8px; border-radius: 3px;
    margin: 2px 2px 2px 0;
}

/* ── Placeholder ── */
.placeholder {
    background: #141413;
    border: 1px dashed #242422;
    border-radius: 8px;
    padding: 3.5rem 2rem;
    text-align: center;
    color: #333;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
}

/* ── Elapsed ── */
.elapsed {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; color: #444;
    text-align: right; margin-top: 1rem;
}

/* ── Complexity dots ── */
.complexity-row {
    display: flex; gap: 4px; margin-top: 4px;
}
.c-dot {
    width: 10px; height: 10px; border-radius: 2px;
}
.c-dot-on-simple  { background: #4ade80; }
.c-dot-on-mod     { background: #fbbf24; }
.c-dot-on-complex { background: #f87171; }
.c-dot-off        { background: #222; }

/* ── Divider ── */
.divider {
    border: none; border-top: 1px solid #222;
    margin: 1rem 0;
}

/* ── Portfolio banner ── */
.portfolio-banner {
    background: #131a13;
    border: 1px solid #2d4a2d;
    border-left: 3px solid #4ade80;
    border-radius: 8px;
    padding: 0.8rem 1.25rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}
.portfolio-banner-text {
    font-size: 0.83rem;
    color: #888;
    line-height: 1.55;
}
.portfolio-banner-text strong { color: #c8c6c0; font-weight: 600; }
.portfolio-links { display: flex; gap: 0.5rem; white-space: nowrap; }
.portfolio-link {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem; font-weight: 500;
    padding: 4px 10px; border-radius: 5px;
    text-decoration: none;
    border: 1px solid #2a2a28;
    color: #666; background: #1a1a18;
    transition: all 0.15s;
}
.portfolio-link:hover { background: #1f2d1f; color: #4ade80; border-color: #2d4a2d; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-indicator"></div>
        <p class="topbar-title">Support Reply Copilot</p>
        <span class="topbar-tag">Internal Tool</span>
    </div>
    <div class="topbar-right">Support Ops · Decision Engine v1.0</div>
</div>
""", unsafe_allow_html=True)

# ── Portfolio banner ─────────────────────────────────────────────────────────
st.markdown("""
<div class="portfolio-banner">
    <div class="portfolio-banner-text">
        👋 <strong>Hey, hiring team!</strong> This is a portfolio project by <strong>Sef Nouri</strong> —
        a working AI tool that simulates how support teams can reduce escalations and improve reply quality
        using LLM-based ticket analysis. It detects sentiment, classifies complexity, recommends deflect vs. escalate,
        and drafts a suggested reply — all before the agent starts typing. Feel free to test it with a real ticket.
    </div>
    <div class="portfolio-links">
        <a class="portfolio-link" href="https://github.com/sefket24/support-reply-copilot" target="_blank">⌥ GitHub</a>
        <a class="portfolio-link" href="https://www.linkedin.com/in/sefketnouri" target="_blank">in LinkedIn</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
total    = st.session_state.total_analyzed
deflected = st.session_state.deflected_count
defl_rate = f"{int(deflected/total*100)}%" if total > 0 else "—"
elapsed_str = f"{st.session_state.last_elapsed:.1f}s" if st.session_state.last_elapsed else "—"

st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-label">Tickets Analyzed</div>
        <div class="stat-value">{total}</div>
        <div class="stat-sub">this session</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Deflection Rate</div>
        <div class="stat-value">{defl_rate}</div>
        <div class="stat-sub">resolved without escalation</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Last Analysis</div>
        <div class="stat-value">{elapsed_str}</div>
        <div class="stat-sub">processing time</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Model</div>
        <div class="stat-value" style="font-size:0.9rem;padding-top:0.3rem">Claude<br>Sonnet</div>
        <div class="stat-sub">via Anthropic API</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

CATEGORIES = [
    "Auto-detect",
    "How-to / Feature question",
    "Bug report",
    "Billing / Subscription",
    "Account access",
    "Data / Export",
    "Performance / Outage",
    "Cancellation request",
    "Unclear / Other",
]

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">Incoming ticket</div>', unsafe_allow_html=True)

    category = st.selectbox("Issue category", CATEGORIES)
    message = st.text_area(
        "Customer message",
        placeholder="Paste the customer message here...",
        height=220,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("⚡ Analyze ticket")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
def analyze_ticket(message: str, category: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("ANTHROPIC_API_KEY not found.")
        st.stop()

    client = Anthropic(api_key=api_key)

    cat_context = f" (Agent-tagged category: {category})" if category != "Auto-detect" else ""

    prompt = f"""You are a senior support engineer helping triage incoming support tickets. Analyze the ticket below and return ONLY valid JSON — no markdown fences, no preamble.

Ticket{cat_context}:
\"\"\"
{message}
\"\"\"

Return exactly this JSON structure:
{{
  "sentiment": "neutral" | "frustrated" | "urgent",
  "complexity": "simple" | "moderate" | "complex",
  "request_type": "how-to" | "bug" | "billing" | "account" | "data" | "performance" | "cancellation" | "unclear",
  "deflection_decision": "deflect" | "human",
  "deflection_reason": "one sentence explaining why this can or cannot be deflected",
  "escalation_flags": ["flag1", "flag2"],
  "confidence": <integer 0-100>,
  "suggested_reply": "A clear, warm, professional reply a support agent would be proud to send. Avoid corporate speak. Be specific and actionable. 3–5 sentences.",
  "internal_note": "One sentence note for the agent — anything worth flagging that the customer won't see.",
  "tags": ["tag1", "tag2", "tag3"]
}}

Rules:
- deflection_decision "deflect" = can be resolved with a single clear answer or link, no back-and-forth needed
- deflection_decision "human" = needs investigation, account access, judgment, or multiple exchanges
- escalation_flags: list only real concerns. Examples: "user is threatening cancellation", "possible data loss", "describes billing error over $100", "mentions regulatory concern", "sentiment indicates churn risk". Empty list [] if none.
- confidence: your certainty in the deflection decision (not in the reply quality)
- suggested_reply: write as the agent, not as an AI. No "As an AI..." language. No hollow apologies. Get to the point.
- tags: short lowercase descriptors for ticket routing/tagging
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Output panel ──────────────────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">Analysis output</div>', unsafe_allow_html=True)

    if not submit:
        st.markdown("""
        <div class="placeholder">
            Paste a ticket and click Analyze.<br>
            The copilot will handle the rest.
        </div>
        """, unsafe_allow_html=True)

    else:
        if not message.strip():
            st.warning("Please paste a customer message.")
        else:
            t_start = time.time()

            with st.spinner("Analyzing..."):
                try:
                    result = analyze_ticket(message.strip(), category)
                except json.JSONDecodeError:
                    st.error("Unexpected response format. Try again.")
                    st.stop()
                except Exception as e:
                    st.error(f"API error: {e}")
                    st.stop()

            elapsed = time.time() - t_start
            st.session_state.total_analyzed += 1
            st.session_state.last_elapsed = elapsed
            if result.get("deflection_decision") == "deflect":
                st.session_state.deflected_count += 1

            # ── Sentiment / complexity / type row ──
            sentiment = result.get("sentiment", "neutral")
            complexity = result.get("complexity", "simple")
            req_type = result.get("request_type", "unclear")

            sent_badge = {
                "neutral":    ("badge-gray",   "● Neutral"),
                "frustrated": ("badge-yellow", "▲ Frustrated"),
                "urgent":     ("badge-red",    "■ Urgent"),
            }.get(sentiment, ("badge-gray", sentiment.title()))

            type_badge = {
                "how-to":       ("badge-blue",   "How-to"),
                "bug":          ("badge-red",    "Bug"),
                "billing":      ("badge-yellow", "Billing"),
                "account":      ("badge-blue",   "Account"),
                "data":         ("badge-blue",   "Data"),
                "performance":  ("badge-red",    "Performance"),
                "cancellation": ("badge-yellow", "Cancellation"),
                "unclear":      ("badge-gray",   "Unclear"),
            }.get(req_type, ("badge-gray", req_type.title()))

            # Complexity dots
            dots_map = {
                "simple":   [True, False, False],
                "moderate": [True, True, False],
                "complex":  [True, True, True],
            }
            dot_colors = ["c-dot-on-simple", "c-dot-on-mod", "c-dot-on-complex"]
            dots_state = dots_map.get(complexity, [False, False, False])
            dots_html = "".join(
                f'<div class="c-dot {dot_colors[i] if dots_state[i] else "c-dot-off"}"></div>'
                for i in range(3)
            )

            st.markdown(f"""
            <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:1rem">
                <span class="badge {sent_badge[0]}">{sent_badge[1]}</span>
                <span class="badge {type_badge[0]}">{type_badge[1]}</span>
                <div style="display:flex;align-items:center;gap:6px;margin-left:4px">
                    <span style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#555;text-transform:uppercase;letter-spacing:1px">Complexity</span>
                    <div class="complexity-row">{dots_html}</div>
                    <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#666">{complexity.title()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Deflection decision ──
            defl = result.get("deflection_decision", "human")
            defl_reason = result.get("deflection_reason", "")
            if defl == "deflect":
                defl_label = "✓ Deflect with guidance"
                defl_cls = "deflect"
            else:
                defl_label = "→ Requires human handling"
                defl_cls = "human"

            st.markdown('<div class="section-label">Deflection decision</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="deflection-box {defl_cls}">
                <strong style="font-family:'DM Mono',monospace;font-size:0.78rem">{defl_label}</strong><br>
                <span style="font-size:0.82rem;opacity:0.85">{defl_reason}</span>
            </div>
            """, unsafe_allow_html=True)

            # ── Confidence ──
            confidence = result.get("confidence", 50)
            conf_cls = "conf-high" if confidence >= 75 else ("conf-medium" if confidence >= 45 else "conf-low")
            st.markdown(f"""
            <div style="margin-top:0.9rem">
                <div class="section-label">Decision confidence</div>
                <div class="conf-track">
                    <div class="conf-fill {conf_cls}" style="width:{confidence}%"></div>
                </div>
                <div class="conf-pct">{confidence}%</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Escalation flags ──
            flags = result.get("escalation_flags", [])
            if flags:
                st.markdown('<div class="section-label">Escalation flags</div>', unsafe_allow_html=True)
                flags_html = " ".join(f'<span class="flag-item">⚑ {f}</span>' for f in flags)
                st.markdown(flags_html, unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ── Suggested reply ──
            st.markdown('<div class="section-label">Suggested reply</div>', unsafe_allow_html=True)
            suggested = result.get("suggested_reply", "")
            st.markdown(f'<div class="reply-box">{suggested}</div>', unsafe_allow_html=True)
            st.code(suggested, language=None)

            # ── Internal note ──
            internal_note = result.get("internal_note", "")
            if internal_note:
                st.markdown('<div class="section-label">Internal note (agent only)</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:#1c1c1a;border:1px solid #2a2a28;border-radius:6px;padding:0.7rem 1rem;font-size:0.82rem;color:#666;font-style:italic;line-height:1.6">
                    {internal_note}
                </div>
                """, unsafe_allow_html=True)

            # ── Tags ──
            tags = result.get("tags", [])
            if tags:
                st.markdown('<div class="section-label">Tags</div>', unsafe_allow_html=True)
                st.markdown(" ".join(f'<span class="tag-item">{t}</span>' for t in tags), unsafe_allow_html=True)

            st.markdown(f'<div class="elapsed">⏱ {elapsed:.1f}s</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-family:DM Mono,monospace;font-size:0.65rem;color:#333'>"
    "Support Reply Copilot · Streamlit + Anthropic Claude · Internal Decision Engine"
    "</p>",
    unsafe_allow_html=True,
)
