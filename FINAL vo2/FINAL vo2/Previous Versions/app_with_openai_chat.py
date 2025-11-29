import os
import uuid
from datetime import datetime
import streamlit as st
from openai import OpenAI
import json

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Florida DMV AI Assistant",
    page_icon="🚗",
    layout="wide",
)

# =====================================================
# OPENAI SETUP
# =====================================================
# Initialize OpenAI client with API key
OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================
# DMV KNOWLEDGE BASE
# =====================================================
DMV_SERVICES = {
    "renew_license": {
        "name": "Renew Driver's License",
        "description": "Renew an expiring or expired driver's license",
        "documents": [
            "Current driver's license (or expired within last 12 months)",
            "Proof of identity (passport, birth certificate, or permanent resident card)",
            "Proof of Social Security Number (SSN card, W-2, or paystub)",
            "Two proofs of Florida residential address (utility bill, bank statement, lease agreement)"
        ]
    },
    "new_license": {
        "name": "Get First Driver's License",
        "description": "Apply for your first Florida driver's license",
        "documents": [
            "Proof of identity (certified US birth certificate or valid US passport)",
            "Proof of Social Security Number (SSN card, W-2, or paystub)",
            "Two proofs of Florida residential address",
            "Certificate of completion from Traffic Law & Substance Abuse Education course",
            "Passing score on written knowledge exam",
            "Passing score on driving skills test (if under 18, must hold learner's permit for 12 months)"
        ]
    },
    "register_vehicle": {
        "name": "Register a Vehicle",
        "description": "Register a new or used vehicle in Florida",
        "documents": [
            "Proof of ownership (manufacturer's certificate of origin for new vehicles or title for used vehicles)",
            "Proof of Florida insurance",
            "Valid Florida driver's license or ID",
            "Vehicle Identification Number (VIN) verification",
            "Completed Application for Certificate of Title (Form HSMV 82040)",
            "Payment for registration fees and taxes"
        ]
    },
    "transfer_title": {
        "name": "Transfer Vehicle Title",
        "description": "Transfer ownership of a vehicle",
        "documents": [
            "Current vehicle title properly signed by seller and buyer",
            "Valid Florida driver's license or ID",
            "Proof of Florida insurance",
            "Odometer disclosure statement (if vehicle is less than 10 years old)",
            "Bill of sale or purchase agreement",
            "Payment for title transfer fees"
        ]
    }
}

# =====================================================
# STYLES
# =====================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-header {
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

.chat-container {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    max-height: 500px;
    overflow-y: auto;
}

.user-message {
    background: #e3f2fd;
    padding: 0.8rem 1.2rem;
    border-radius: 15px 15px 5px 15px;
    margin: 0.5rem 0;
    max-width: 70%;
    margin-left: auto;
}

.ai-message {
    background: #f3f4f6;
    padding: 0.8rem 1.2rem;
    border-radius: 15px 15px 15px 5px;
    margin: 0.5rem 0;
    max-width: 70%;
}

.service-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    border: 2px solid #e5e7eb;
    cursor: pointer;
    transition: all 0.3s;
}

.service-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.document-check {
    background: #f0fdf4;
    border: 1px solid #86efac;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    margin: 0.3rem 0;
}

.stButton > button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.5rem 2rem;
    border-radius: 25px;
    font-weight: 600;
    transition: transform 0.2s;
}

.stButton > button:hover {
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Welcome to the Florida DMV AI Assistant! I'm here to help you prepare for your DMV visit. What brings you to the DMV today?\n\nHere are the most common services:\n\n1. 🚗 **Renew Driver's License**\n2. 🆕 **Get First Driver's License**\n3. 📋 **Register a Vehicle**\n4. 📄 **Transfer Vehicle Title**\n\nPlease select an option or tell me what you need help with."
    })

if 'selected_service' not in st.session_state:
    st.session_state.selected_service = None

if 'documents_verified' not in st.session_state:
    st.session_state.documents_verified = False

if 'current_step' not in st.session_state:
    st.session_state.current_step = 'service_selection'

# =====================================================
# AI CHAT FUNCTIONS
# =====================================================
def get_ai_response(user_message, context=""):
    """Get response from OpenAI based on user message and context"""
    try:
        system_prompt = f"""You are a helpful Florida DMV assistant. You help users understand what documents they need for various DMV services.
        
        Current context: {context}
        
        Available services and their requirements:
        {json.dumps(DMV_SERVICES, indent=2)}
        
        Be friendly, clear, and concise. If the user mentions having documents, verify they have all required documents for their selected service.
        If they have all documents, confirm they're ready to book an appointment."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I'm having trouble connecting to the AI service. Error: {str(e)}\n\nPlease try selecting from the options above or describe your DMV needs."

def identify_service_from_message(message):
    """Identify which DMV service the user is asking about"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['renew', 'renewal', 'expir']):
        if 'license' in message_lower or 'driver' in message_lower:
            return 'renew_license'
    elif any(word in message_lower for word in ['first', 'new', 'learner', 'permit']):
        if 'license' in message_lower or 'driver' in message_lower:
            return 'new_license'
    elif any(word in message_lower for word in ['register', 'registration']):
        if 'vehicle' in message_lower or 'car' in message_lower:
            return 'register_vehicle'
    elif any(word in message_lower for word in ['transfer', 'title', 'sell', 'buy']):
        if 'vehicle' in message_lower or 'car' in message_lower or 'title' in message_lower:
            return 'transfer_title'
    
    # Check for numbered selections
    if '1' in message or 'renew driver' in message_lower:
        return 'renew_license'
    elif '2' in message or 'first driver' in message_lower:
        return 'new_license'
    elif '3' in message or 'register vehicle' in message_lower:
        return 'register_vehicle'
    elif '4' in message or 'transfer' in message_lower:
        return 'transfer_title'
    
    return None

def check_documents_mentioned(message, service_key):
    """Check if user has mentioned they have the required documents"""
    message_lower = message.lower()
    
    # Keywords that suggest user has documents
    confirmation_words = ['yes', 'have', 'got', 'ready', 'all set', 'prepared', 'collected', 'gathered']
    document_words = ['documents', 'papers', 'everything', 'requirements', 'docs']
    
    has_confirmation = any(word in message_lower for word in confirmation_words)
    mentions_documents = any(word in message_lower for word in document_words)
    
    return has_confirmation and mentions_documents

# =====================================================
# MAIN APP INTERFACE
# =====================================================

# Header
st.markdown("""
<div class="main-header">
    <h1 style="color: #1f2937; margin: 0;">🚗 Florida DMV AI Assistant</h1>
    <p style="color: #6b7280; margin-top: 0.5rem;">Get prepared for your DMV visit with our intelligent document checker</p>
</div>
""", unsafe_allow_html=True)

# Create two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat with DMV Assistant")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
    
    # User input
    user_input = st.text_input("Type your message here...", key="user_input", placeholder="E.g., 'I need to renew my driver's license'")
    
    if st.button("Send", key="send_button"):
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Process based on current step
            if st.session_state.current_step == 'service_selection':
                # Try to identify service
                service = identify_service_from_message(user_input)
                
                if service:
                    st.session_state.selected_service = service
                    st.session_state.current_step = 'document_check'
                    
                    # Get service details
                    service_info = DMV_SERVICES[service]
                    
                    # Create response with document requirements
                    response = f"Great! You want to **{service_info['name']}**.\n\n"
                    response += "📋 **Required Documents:**\n\n"
                    for i, doc in enumerate(service_info['documents'], 1):
                        response += f"{i}. {doc}\n"
                    response += "\n✅ **Do you have all these documents ready?** Please let me know if you have everything or if you need help obtaining any of these documents."
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    # Use AI to understand the request
                    ai_response = get_ai_response(user_input, "User is selecting a DMV service")
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            elif st.session_state.current_step == 'document_check':
                # Check if user confirms having documents
                if check_documents_mentioned(user_input, st.session_state.selected_service):
                    st.session_state.documents_verified = True
                    st.session_state.current_step = 'ready_to_book'
                    
                    response = """🎉 **Excellent! You're all set!**

✅ All required documents verified
✅ Ready for your DMV visit

**Next Steps:**
1. 📅 **Book Your Appointment**: Visit [MyDMV Portal](https://mydmvportal.flhsmv.gov/) to schedule your appointment
2. 🕐 **Arrive Early**: Get there 15 minutes before your scheduled time
3. 💳 **Payment Ready**: Bring cash, check, or card for any applicable fees
4. 📱 **Save Confirmation**: Keep your appointment confirmation number handy

**Quick Tips:**
- Most DMV offices are less crowded early morning (8-9 AM) or late afternoon
- Consider visiting mid-week (Tuesday-Thursday) for shorter wait times
- Some services may be available online - check the portal first!

Is there anything else you'd like to know about your DMV visit?"""
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    # Help user with missing documents
                    ai_response = get_ai_response(
                        user_input, 
                        f"User needs to verify documents for {DMV_SERVICES[st.session_state.selected_service]['name']}"
                    )
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            elif st.session_state.current_step == 'ready_to_book':
                # Answer any follow-up questions
                ai_response = get_ai_response(
                    user_input,
                    f"User is ready to book appointment for {DMV_SERVICES[st.session_state.selected_service]['name']}"
                )
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            st.rerun()

with col2:
    st.subheader("📊 Current Status")
    
    # Status indicators
    if st.session_state.selected_service:
        service_info = DMV_SERVICES[st.session_state.selected_service]
        
        st.info(f"**Selected Service:**\n{service_info['name']}")
        
        st.write("**Required Documents:**")
        for doc in service_info['documents']:
            if st.session_state.documents_verified:
                st.success(f"✅ {doc}")
            else:
                st.warning(f"⏳ {doc}")
        
        if st.session_state.documents_verified:
            st.balloons()
            st.success("🎉 Ready to book your appointment!")
            st.markdown("[**Book Appointment Now →**](https://mydmvportal.flhsmv.gov/)")
    else:
        st.info("💡 Select a service to see requirements")
    
    # Reset button
    if st.button("🔄 Start Over", key="reset"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "👋 Welcome to the Florida DMV AI Assistant! I'm here to help you prepare for your DMV visit. What brings you to the DMV today?\n\nHere are the most common services:\n\n1. 🚗 **Renew Driver's License**\n2. 🆕 **Get First Driver's License**\n3. 📋 **Register a Vehicle**\n4. 📄 **Transfer Vehicle Title**\n\nPlease select an option or tell me what you need help with."
        }]
        st.session_state.selected_service = None
        st.session_state.documents_verified = False
        st.session_state.current_step = 'service_selection'
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
    <p>🏛️ Florida Department of Highway Safety and Motor Vehicles</p>
    <p>This AI assistant helps you prepare for your visit. Always verify requirements on the official website.</p>
</div>
""", unsafe_allow_html=True)
