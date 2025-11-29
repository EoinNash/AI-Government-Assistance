import os
import uuid
from datetime import datetime

import streamlit as st

# Try to import the CNN classifier
try:
    from form_classifier import classify_form_image, FormClassifier
    CNN_AVAILABLE = True
except ImportError:
    CNN_AVAILABLE = False

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="FormPilot TT + AI Vision",
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

/* Prediction card */
.prediction-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 2px solid #0ea5e9;
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem 0;
}

.prediction-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #0c4a6e;
    margin-bottom: 0.5rem;
}

.confidence-bar {
    background: #e0f2fe;
    border-radius: 8px;
    height: 30px;
    position: relative;
    overflow: hidden;
}

.confidence-fill {
    background: linear-gradient(90deg, #0ea5e9 0%, #0284c7 100%);
    height: 100%;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
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
# FORM DATABASE MAPPING
# =====================================================
FORM_DATABASE = {
    'drivers_license': {
        "title": "Driver's Permit Renewal (Trinidad & Tobago)",
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
            {"label": "Driver's Permit Renewal Form (PDF)", "url": "#"},
            {"label": "Licensing Division Information", "url": "#"},
        ],
        "notes": "Renewals must currently be done in person.",
    },
    'vehicle_registration': {
        "title": "Vehicle Registration Renewal",
        "agency": "Licensing Division, Ministry of Works and Transport",
        "est_wait": "1–2 hours",
        "fee": "TT$150–TT$300",
        "requirements": [
            "Current vehicle registration certificate",
            "Valid insurance certificate",
            "Inspection certificate (if applicable)",
            "Proof of address",
        ],
        "steps": [
            "Ensure vehicle inspection is up to date.",
            "Gather required documents.",
            "Visit Licensing Office.",
            "Submit documents and pay renewal fee.",
            "Collect new registration certificate.",
        ],
        "links": [
            {"label": "Vehicle Registration Info", "url": "#"},
        ],
        "notes": "Must be done before expiration date.",
    },
    'vehicle_title': {
        "title": "Vehicle Title Transfer",
        "agency": "Licensing Division, Ministry of Works and Transport",
        "est_wait": "2–5 business days",
        "fee": "TT$200–TT$400",
        "requirements": [
            "Original vehicle title",
            "Bill of sale",
            "Valid ID of buyer and seller",
            "Proof of insurance",
        ],
        "steps": [
            "Complete title transfer form.",
            "Both parties sign the form.",
            "Submit to Licensing Office with documents.",
            "Pay transfer fee.",
            "Receive new title in buyer's name.",
        ],
        "links": [
            {"label": "Title Transfer Form", "url": "#"},
        ],
        "notes": "Both parties should be present.",
    },
    'building_permit': {
        "title": "Building Permit Application",
        "agency": "Regional Corporation / Municipal Corporation",
        "est_wait": "2–6 weeks",
        "fee": "TT$500–TT$5000 (depends on project size)",
        "requirements": [
            "Completed application form",
            "Architectural drawings",
            "Land survey",
            "Proof of property ownership",
            "Engineer's report (for larger structures)",
        ],
        "steps": [
            "Hire architect to prepare drawings.",
            "Submit application with all documents.",
            "Pay application fee.",
            "Await inspection and approval.",
            "Collect permit once approved.",
        ],
        "links": [
            {"label": "Building Permit Application", "url": "#"},
        ],
        "notes": "Processing time varies by region.",
    },
    'state_id': {
        "title": "National ID Card Application",
        "agency": "Registration Division, Ministry of Legal Affairs",
        "est_wait": "2–4 weeks",
        "fee": "Free for first-time applicants; TT$50 for replacement",
        "requirements": [
            "Birth certificate",
            "Proof of address",
            "Two passport photos",
            "Completed application form",
        ],
        "steps": [
            "Visit Registration Office.",
            "Complete application form.",
            "Submit documents and photos.",
            "Have biometrics taken.",
            "Collect ID card when ready.",
        ],
        "links": [
            {"label": "National ID Info", "url": "#"},
        ],
        "notes": "Appointment may be required.",
    }
}

# =====================================================
# DEMO RULE-BASED FORM LOOKUP
# =====================================================
def get_form_info_demo(message: str):
    """Deterministic 'fake AI' for demo use."""
    m = message.lower()
    if "driver" in m or "license" in m:
        return FORM_DATABASE['drivers_license']
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
            "notes": "Appointments are required for some offices.",
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
    
    # Default to vehicle registration
    return FORM_DATABASE['vehicle_registration']

def get_form_info_by_type(form_type: str):
    """Get form info by CNN prediction"""
    return FORM_DATABASE.get(form_type, FORM_DATABASE['vehicle_registration'])

# =====================================================
# LLM FUNCTION (OPTIONAL)
# =====================================================
def call_llm_openai(user_message: str, history: list):
    """Optional OpenAI integration"""
    try:
        from openai import OpenAI
    except ImportError:
        return "LLM not available (openai package not installed)."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "LLM not available (OPENAI_API_KEY not set)."

    client = OpenAI(api_key=api_key)
    
    system_prompt = (
        "You are an assistant that helps citizens of Trinidad & Tobago find the correct "
        "government form and understand requirements and steps. "
        "Keep answers concise and practical."
    )

    convo_text = "Previous questions:\n" + "\n".join(f"- {m}" for m in history[-5:]) + \
                 f"\n\nUser question: {user_message}"

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"{system_prompt}\n\n{convo_text}",
    )
    
    try:
        llm_text = response.output_text
    except AttributeError:
        first = response.output[0].content[0].text
        llm_text = first

    return llm_text

# =====================================================
# SESSION STATE
# =====================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_form" not in st.session_state:
    st.session_state.current_form = None
if "ai_notes" not in st.session_state:
    st.session_state.ai_notes = ""
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex
if "cnn_prediction" not in st.session_state:
    st.session_state.cnn_prediction = None

# =====================================================
# HERO
# =====================================================
st.markdown(
    """
<div class="hero">
  <div class="hero-title">🤖 FormPilot TT + AI Vision</div>
  <div class="hero-sub">
    Chat assistant + CNN-powered form image recognition for Trinidad & Tobago government forms
  </div>
  <div class="hero-pill">
    Demo build • CNN Model Integrated
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================
# SIDEBAR: CONTROLS
# =====================================================
with st.sidebar:
    st.subheader("🎯 Mode")
    mode = st.radio(
        "Select input mode:",
        ["💬 Chat (Text)", "🖼️ Image Upload (CNN)"],
        index=0
    )
    
    use_llm = st.toggle("Use OpenAI LLM (live)", value=False,
                        help="Off = demo rules. On = call OpenAI API (requires key).")
    
    st.markdown("---")
    
    if mode == "💬 Chat (Text)":
        st.subheader("Quick prompts")
        examples = [
            "I need to renew my driver's permit",
            "How do I renew my passport?",
            "Vehicle registration renewal",
            "How do I get a BIR number?",
        ]
        for ex in examples:
            if st.button(ex, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": ex})
                info = get_form_info_demo(ex)
                st.session_state.current_form = info
                st.session_state.cnn_prediction = None

                history_texts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
                if use_llm:
                    ai_text = call_llm_openai(ex, history_texts)
                else:
                    ai_text = "Demo mode: using built-in rules."

                st.session_state.ai_notes = ai_text
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Here's what I found for **{info['title']}**.",
                })
                st.rerun()
    else:
        st.subheader("📸 Upload Form Image")
        st.caption("Upload a government form image for CNN classification")
        
        if not CNN_AVAILABLE:
            st.error("⚠️ CNN classifier not available. Make sure form_classifier.py is in the same directory.")
    
    st.markdown("---")
    st.caption(f"Session ID: {st.session_state.session_id[:8]}")

# =====================================================
# MAIN LAYOUT
# =====================================================
col_left, col_right = st.columns([0.55, 0.45])

# ---------- LEFT: INPUT AREA ----------
with col_left:
    if mode == "💬 Chat (Text)":
        st.markdown("#### 💬 Conversation")
        
        st.markdown('<div class="card chat-scroll">', unsafe_allow_html=True)
        
        for msg in st.session_state.messages:
            avatar = "🧑" if msg["role"] == "user" else "🧑🏽‍💼"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        mode_label = "Live LLM (OpenAI)" if use_llm else "Demo rules"
        st.markdown(f"<div class='status-line'>Mode: <b>{mode_label}</b></div>", unsafe_allow_html=True)
        
        user_text = st.chat_input("Ask about a form...")
        if user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})
            info = get_form_info_demo(user_text)
            st.session_state.current_form = info
            st.session_state.cnn_prediction = None

            history_texts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
            if use_llm:
                ai_text = call_llm_openai(user_text, history_texts)
            else:
                ai_text = "Demo mode: response from pre-defined rules."

            st.session_state.ai_notes = ai_text
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Found details for **{info['title']}**.",
            })
            st.rerun()
    
    else:  # Image Upload Mode
        st.markdown("#### 🖼️ Image Recognition")
        
        uploaded_file = st.file_uploader(
            "Upload a government form image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear image of a government form"
        )
        
        if uploaded_file is not None:
            # Display image
            st.image(uploaded_file, caption="Uploaded Form", use_container_width=True)
            
            if st.button("🔍 Classify Form", type="primary", use_container_width=True):
                if CNN_AVAILABLE:
                    with st.spinner("🤖 Running CNN classification..."):
                        try:
                            # Read image bytes
                            image_bytes = uploaded_file.read()
                            
                            # Classify
                            result = classify_form_image(image_bytes, 'form_classifier_model.keras')
                            
                            st.session_state.cnn_prediction = result
                            
                            # Get form info based on prediction
                            form_type = result['form_type']
                            info = get_form_info_by_type(form_type)
                            st.session_state.current_form = info
                            
                            st.success("✅ Classification complete!")
                            st.rerun()
                            
                        except FileNotFoundError:
                            st.error("❌ Model file not found! Please train the model first by running: `python train_model.py`")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("CNN classifier not available!")
        
        # Show prediction results if available
        if st.session_state.cnn_prediction:
            result = st.session_state.cnn_prediction
            
            st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="prediction-title">🎯 Prediction: {result["form_type"].replace("_", " ").title()}</div>', unsafe_allow_html=True)
            
            confidence_pct = result['confidence'] * 100
            st.markdown(f"""
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence_pct}%">
                        {confidence_pct:.1f}% confident
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Show all probabilities
            with st.expander("📊 All Probabilities"):
                for form_type, prob in sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True):
                    st.progress(prob, text=f"{form_type.replace('_', ' ').title()}: {prob*100:.1f}%")

# ---------- RIGHT: FORM DETAILS ----------
with col_right:
    st.markdown("#### 📋 Form Details")
    details = st.session_state.current_form

    if details:
        # Overview card
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
                st.write("No specific links available.")
            st.caption(f"Generated • {datetime.now().strftime('%b %d, %Y • %I:%M %p')}")

        with tab3:
            if st.session_state.ai_notes:
                st.markdown(st.session_state.ai_notes)
            else:
                st.write("No AI notes yet.")

    else:
        st.markdown(
            """
<div class="card">
  No form selected yet. Ask a question in chat or upload a form image for CNN classification.
</div>
""",
            unsafe_allow_html=True,
        )

# =====================================================
# FOOTER
# =====================================================
st.markdown(
    "<div class='footer'>FormPilot TT + AI Vision • CNN Model Integrated • Demo by Giovanny Victome</div>",
    unsafe_allow_html=True,
)
