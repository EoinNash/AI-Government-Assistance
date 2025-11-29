import os
import uuid
from datetime import datetime

import streamlit as st

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="FormPilot TT",
    page_icon="📄",
    layout="wide",
)

# =====================================================
# STYLES
# =====================================================
st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] {
    background: #f3f4f6;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #eef2ff 0%, #e0f2fe 50%, #fef2f2 100%);
    padding: 1.5rem 1.8rem;
    margin: -1rem -1rem 1rem -1rem;
    border-bottom: 1px solid #e5e7eb;
}
.hero-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #111827;
}
.hero-sub {
    margin-top: 0.15rem;
    color: #4b5563;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(37,99,235,0.1);
    border-radius: 999px;
    padding: 0.25rem 0.7rem;
    font-size: 0.8rem;
    color: #1d4ed8;
    border: 1px solid rgba(37,99,235,0.35);
    margin-top: 0.5rem;
}

/* Cards */
.card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 18px rgba(15,23,42,0.05);
    padding: 1rem 1.2rem;
}

/* Key/Value */
.kv {
    display: grid;
    grid-template-columns: 140px 1fr;
    gap: 0.4rem 0.75rem;
    font-size: 0.94rem;
}
.kv .k { color: #6b7280; }

/* Chat scroll area */
.chat-scroll {
    max-height: 420px;
    overflow-y: auto;
    padding-right: 0.3rem;
}

/* Status line */
.status-line {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

/* Footer */
.footer {
    margin-top: 0.8rem;
    text-align: center;
    color: #6b7280;
    font-size: 0.85rem;
}

/* ----- TAB FIXES (Make tabs visible + bold) ----- */
.stTabs [data-baseweb="tab-list"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    padding: 0.35rem 0.5rem !important;
    margin-bottom: 0.5rem !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: #ffffff !important;
    color: #4b5563 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.35rem 0.8rem !important;
    margin-right: 0.3rem !important;
    border: 1px solid transparent !important;
}

.stTabs [aria-selected="true"] {
    background-color: #e0ecff !important;
    color: #1d4ed8 !important;
    border: 1px solid #93c5fd !important;
    font-weight: 700 !important;
}


</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# DEMO RULE-BASED FORM LOOKUP
# =====================================================
def get_form_info_demo(message: str):
    """Deterministic 'fake AI' for demo use."""
    m = message.lower()
    if "driver" in m:
        return {
            "title": "Driver’s Permit Renewal (Trinidad & Tobago)",
            "agency": "Licensing Division, Ministry of Works and Transport",
            "est_wait": "Same-day service if early; 1–2 hours average queue time",
            "fee": "TT$80–TT$500 depending on permit class",
            "requirements": [
                "Existing driver's permit",
                "Two (2) passport-sized photos (if photo update required)",
                "Proof of address (utility bill, bank statement, etc.)",
                "Completed Renewal Application Form (Form 4)",
            ],
            "steps": [
                "Visit your nearest Licensing Office (e.g., Caroni, Wrightson Road).",
                "Collect or download and complete the Renewal Form.",
                "Submit form and documents to the clerk.",
                "Pay the renewal fee at the cashier.",
                "Take a new photo (if required) and collect your updated permit.",
            ],
            "links": [
                {"label": "Driver’s Permit Renewal Form (PDF)", "url": "#"},
                {"label": "Licensing Division Information", "url": "#"},
            ],
            "notes": "Renewals must currently be done in person.",
        }
    if "passport" in m:
        return {
            "title": "Passport Renewal Application",
            "agency": "Immigration Division, Ministry of National Security",
            "est_wait": "7–14 working days (standard) or ~3 days (express)",
            "fee": "TT$250 (standard) • TT$500 (express)",
            "requirements": [
                "Completed Passport Application Form",
                "Old passport",
                "Two (2) passport-sized photos",
                "Birth certificate and a valid photo ID",
            ],
            "steps": [
                "Collect or download the Passport Application Form.",
                "Complete and sign the form.",
                "Submit form and documents at the Immigration Office.",
                "Pay the applicable fee and keep your receipt.",
                "Return on the date indicated to collect your renewed passport.",
            ],
            "links": [
                {"label": "Passport Application Form (PDF)", "url": "#"},
                {"label": "Immigration Division Website", "url": "#"},
            ],
            "notes": "Appointments are required for some offices (e.g. Port of Spain, San Fernando).",
        }
    if "bir" in m or "tax" in m:
        return {
            "title": "BIR Number Registration (Individuals)",
            "agency": "Board of Inland Revenue (BIR), Ministry of Finance",
            "est_wait": "3–5 business days",
            "fee": "Free",
            "requirements": [
                "Completed Application Form (Form 1)",
                "National ID or passport",
                "Proof of address",
            ],
            "steps": [
                "Visit a Regional Revenue Office or BIR Head Office.",
                "Complete Form 1 (Application for BIR Number).",
                "Submit the form with ID and proof of address.",
                "Await notification and collect your BIR number.",
            ],
            "links": [
                {"label": "BIR Registration Form (Form 1 PDF)", "url": "#"},
            ],
            "notes": "Once issued, your BIR number is used for all tax-related filings.",
        }
    if "wasa" in m or "water" in m:
        return {
            "title": "WASA New Water Connection",
            "agency": "Water and Sewerage Authority (WASA)",
            "est_wait": "5–10 business days after inspection",
            "fee": "Typically TT$600–TT$1200 depending on work required",
            "requirements": [
                "Completed WASA New Connection Application",
                "Proof of property ownership or rental agreement",
                "Valid ID of the applicant",
                "Recent utility bill (if available)",
            ],
            "steps": [
                "Collect or download the New Connection Application form.",
                "Submit form and documents at your regional WASA office.",
                "Pay the connection estimate/fee.",
                "WASA conducts a site inspection.",
                "Once approved, connection works are carried out and service begins.",
            ],
            "links": [
                {"label": "WASA New Connection Form (PDF)", "url": "#"},
            ],
            "notes": "Ensure there is an approved service point on the property line.",
        }
    if "vehicle" in m and "registration" in m:
        return {
            "title": "Vehicle Registration Renewal",
            "agency": "Licensing Division, Ministry of Works and Transport",
            "est_wait": "1–3 business days (depending on inspection and office)",
            "fee": "TT$100–TT$250 depending on vehicle type",
            "requirements": [
                "Valid insurance certificate",
                "Valid inspection certificate (for vehicles over 5 years old)",
                "Existing Certificate of Registration",
                "Completed Vehicle Registration Renewal Form",
            ],
            "steps": [
                "Ensure vehicle inspection and insurance are both up to date.",
                "Complete the Vehicle Registration Renewal Form.",
                "Submit form and documents at the Licensing Office.",
                "Pay the renewal fee.",
                "Collect the updated Certificate of Registration.",
            ],
            "links": [
                {"label": "Vehicle Registration Renewal Form (PDF)", "url": "#"},
            ],
            "notes": "You may need to present the vehicle for inspection in some cases.",
        }

    # Fallback
    return {
        "title": "General Government Form Assistance",
        "agency": "Government of Trinidad & Tobago",
        "est_wait": "Varies by ministry/department",
        "fee": "Varies",
        "requirements": [
            "Completed application form",
            "Valid ID",
            "Supporting documents listed on the form",
        ],
        "steps": [
            "Identify the correct ministry/agency for your need.",
            "Download or collect the relevant form.",
            "Fill out the form and attach supporting documents.",
            "Submit at the specified office or collection point.",
        ],
        "links": [
            {"label": "Government Forms Directory", "url": "#"},
        ],
        "notes": "Always double-check requirements on the ministry’s official website.",
    }

# =====================================================
# OPTIONAL: REAL LLM CALL (OpenAI)
# =====================================================
def call_llm_openai(user_message: str, history: list[str]) -> str:
    """
    🔌 Plug-in point for a real LLM.

    Requires:
      - `pip install openai`
      - OPENAI_API_KEY env var set

    Uses the Responses API (recommended) with a small model
    to keep costs down. :contentReference[oaicite:1]{index=1}
    """
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        return "LLM not available (openai package not installed). Using demo rules instead."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "LLM not available (OPENAI_API_KEY not set). Using demo rules instead."

    client = OpenAI(api_key=api_key)

    # You can tune model: gpt-4.1-mini / gpt-4o-mini etc.
    system_prompt = (
        "You are an assistant that helps citizens of Trinidad & Tobago find the correct "
        "government form and understand requirements and steps. "
        "Keep answers concise and practical."
    )

    # We keep it simple: current question + a short history string.
    convo_text = "Previous questions:\n" + "\n".join(f"- {m}" for m in history[-5:]) + \
                 f"\n\nUser question: {user_message}"

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"{system_prompt}\n\n{convo_text}",
    )
    # The docs expose a convenience property `output_text` for plain text. :contentReference[oaicite:2]{index=2}
    try:
        llm_text = response.output_text
    except AttributeError:
        # Fallback if that helper is not present for some reason
        first = response.output[0].content[0].text
        llm_text = first

    return llm_text

# =====================================================
# SESSION STATE
# =====================================================
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{role, content}]
if "current_form" not in st.session_state:
    st.session_state.current_form = None
if "ai_notes" not in st.session_state:
    st.session_state.ai_notes = ""
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex

# =====================================================
# HERO
# =====================================================
st.markdown(
    """
<div class="hero">
  <div class="hero-title">FormPilot TT</div>
  <div class="hero-sub">
    A demo assistant that helps Trinidad & Tobago citizens figure out which government form they need,
    what documents to bring, and what steps to follow.
  </div>
  <div class="hero-pill">
    Demo build • Not an official government service
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================
# SIDEBAR: DEMO CONTROLS
# =====================================================
with st.sidebar:
    st.subheader("Mode")
    use_llm = st.toggle("Use OpenAI LLM (live)", value=False,
                        help="Off = demo rules (no cost). On = call OpenAI API (requires key).")

    st.subheader("Quick prompts")
    examples = [
        "I need to renew my driver's permit",
        "How do I renew my passport?",
        "I want a new WASA connection",
        "How do I get a BIR number?",
        "Renew my vehicle registration",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": ex})
            # In demo, we always map to a structured form:
            info = get_form_info_demo(ex)
            st.session_state.current_form = info

            # Optionally call LLM for explanation/commentary
            history_texts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
            if use_llm:
                ai_text = call_llm_openai(ex, history_texts)
            else:
                ai_text = "Demo mode: using built-in rules (no live LLM call)."

            st.session_state.ai_notes = ai_text
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Here’s what I found for **{info['title']}**. See the details on the right.",
            })
            st.experimental_rerun()

    st.markdown("---")
    st.caption("Toggle LLM on for a real model call.\nDemo mode is safe for classroom / live demos.")

# =====================================================
# MAIN LAYOUT – LEFT CHAT / RIGHT DETAILS
# =====================================================
col_chat, col_details = st.columns([0.55, 0.45])

# ---------- LEFT: CHAT ----------
with col_chat:
    st.markdown("#### Conversation")

    st.markdown('<div class="card chat-scroll">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        avatar = "🧍" if msg["role"] == "user" else "🧑🏽‍💼"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

    # Status line under history
    mode_label = "Live LLM (OpenAI)" if use_llm else "Demo rules (no API calls)"
    st.markdown(f"<div class='status-line'>Mode: <b>{mode_label}</b></div>", unsafe_allow_html=True)

    # Chat input
    user_text = st.chat_input(
        "Ask about a form (e.g. “passport renewal”, “driver’s permit”, “WASA connection”)"
    )
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})

        # Always derive a structured form from the rules for now
        info = get_form_info_demo(user_text)
        st.session_state.current_form = info

        # LLM commentary (optional)
        history_texts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        if use_llm:
            ai_text = call_llm_openai(user_text, history_texts)
        else:
            ai_text = "Demo mode: this response and form mapping come from pre-defined rules."

        st.session_state.ai_notes = ai_text

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"I found details for **{info['title']}**. See the panel on the right.",
        })
        st.rerun()

# ---------- RIGHT: FORM DETAILS ----------
with col_details:
    st.markdown("#### Form details")
    details = st.session_state.current_form

    if details:
        # Overview
        st.markdown(
            f"""
<div class="card">
  <h4 style="margin-top:0;">{details['title']}</h4>
  <div class="kv" style="margin-top:0.6rem;">
    <div class="k">Agency</div><div class="v">{details['agency']}</div>
    <div class="k">Est. wait</div><div class="v">{details['est_wait']}</div>
    <div class="k">Fee</div><div class="v">{details['fee']}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        tab1, tab2, tab3 = st.tabs(["Requirements & Steps", "Forms & Links", "AI Notes"])

        with tab1:
            st.markdown("**Requirements**")
            for r in details["requirements"]:
                st.markdown(f"- {r}")

            st.markdown("**Steps**")
            for i, step in enumerate(details["steps"], start=1):
                st.markdown(f"{i}. {step}")

        with tab2:
            if details.get("links"):
                st.markdown("**Forms & Links**")
                for link in details["links"]:
                    st.markdown(f"- [{link['label']}]({link['url']})")
            else:
                st.write("No specific links available for this form.")
            st.caption(f"Generated • {datetime.now().strftime('%b %d, %Y • %I:%M %p')}")

        with tab3:
            if st.session_state.ai_notes:
                st.markdown(st.session_state.ai_notes)
            else:
                st.write("No AI notes yet. Ask a question or turn on the LLM toggle.")

    else:
        st.markdown(
            """
<div class="card">
  No form selected yet. Ask something in the chat on the left, or use a quick prompt in the sidebar.
</div>
""",
            unsafe_allow_html=True,
        )

# =====================================================
# FOOTER
# =====================================================
st.markdown(
    "<div class='footer'>FormPilot TT • Frontend demo by Gabriel McLean (rules + optional OpenAI LLM)</div>",
    unsafe_allow_html=True,
)
