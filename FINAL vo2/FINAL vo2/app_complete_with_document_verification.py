import os
import uuid
from datetime import datetime
import streamlit as st
from openai import OpenAI
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import random

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Florida DMV AI Assistant - Complete",
    page_icon="🚗",
    layout="wide",
)

# =====================================================
# OPENAI SETUP
# =====================================================
OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================
# FORM CLASSIFIER MODEL
# =====================================================
class FormClassifier:
    """CNN-based classifier for government forms"""
    
    def __init__(self):
        self.img_size = (128, 128)
        self.form_categories = [
            'drivers_license',
            'vehicle_registration', 
            'vehicle_title',
            'building_permit',
            'state_id'
        ]
        self.model = None
        
    def build_model(self):
        """Build the CNN architecture"""
        model = models.Sequential([
            layers.Input(shape=(128, 128, 1)),
            layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dense(5, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def create_distinctive_form(self, form_type, seed=None):
        """Create synthetic form image for demonstration"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        img = Image.new('L', self.img_size, color=255)
        draw = ImageDraw.Draw(img)
        
        if form_type == 'drivers_license':
            draw.rectangle([10, 10, 50, 50], outline=0, width=2)
            for y in range(60, 120, 10):
                draw.line([10, y, 118, y], fill=0, width=1)
                
        elif form_type == 'vehicle_registration':
            for x in range(10, 120, 20):
                draw.line([x, 10, x, 118], fill=0, width=1)
            for y in range(10, 120, 20):
                draw.line([10, y, 118, y], fill=0, width=1)
                
        elif form_type == 'vehicle_title':
            draw.rectangle([10, 10, 60, 60], outline=0, width=3)
            draw.rectangle([68, 10, 118, 60], outline=0, width=3)
            draw.line([10, 70, 118, 118], fill=0, width=3)
            
        elif form_type == 'building_permit':
            draw.rectangle([10, 10, 118, 30], fill=0)
            for x in range(20, 110, 15):
                draw.rectangle([x, 40, x+8, 118], fill=0)
                
        elif form_type == 'state_id':
            draw.rectangle([15, 15, 113, 113], outline=0, width=3)
            draw.ellipse([45, 45, 83, 83], outline=0, width=2)
        
        img_array = np.array(img)
        noise = np.random.normal(0, 10, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        return img_array
    
    def create_training_data(self, samples_per_category=20):
        """Generate synthetic training dataset"""
        X = []
        y = []
        
        for idx, form_type in enumerate(self.form_categories):
            for i in range(samples_per_category):
                img = self.create_distinctive_form(form_type, seed=idx*1000 + i)
                X.append(img)
                y.append(idx)
        
        X = np.array(X).reshape(-1, 128, 128, 1) / 255.0
        y = np.array(y)
        
        return X, y
    
    def quick_train(self):
        """Quick training for demo purposes"""
        X, y = self.create_training_data(samples_per_category=20)
        
        if self.model is None:
            self.build_model()
        
        # Quick training for demo
        self.model.fit(X, y, epochs=10, batch_size=16, verbose=0)
        return True
    
    def predict_form(self, image_input):
        """Predict form type from image"""
        if self.model is None:
            return None
        
        # Handle different input types
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            image = Image.fromarray(image_input)
        
        # Convert to grayscale and resize
        image = image.convert('L')
        image = image.resize(self.img_size)
        
        # Normalize
        img_array = np.array(image).reshape(1, 128, 128, 1) / 255.0
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_idx]
        
        # Create probability dict
        probabilities = {
            form_type: float(prob) 
            for form_type, prob in zip(self.form_categories, predictions[0])
        }
        
        return {
            'form_type': self.form_categories[predicted_idx],
            'confidence': float(confidence),
            'probabilities': probabilities
        }

# =====================================================
# DOCUMENT MAPPING AND DMV KNOWLEDGE BASE
# =====================================================

# Map form types to document categories
FORM_TO_DOCUMENT_MAP = {
    'drivers_license': ['Current driver\'s license', 'Proof of identity'],
    'state_id': ['Proof of identity', 'Florida ID'],
    'vehicle_registration': ['Vehicle registration', 'Proof of Florida insurance'],
    'vehicle_title': ['Vehicle title', 'Proof of ownership'],
    'building_permit': ['Building permit', 'Proof of Florida residential address']
}

DMV_SERVICES = {
    "renew_license": {
        "name": "Renew Driver's License",
        "description": "Renew an expiring or expired driver's license",
        "documents": [
            "Current driver's license",
            "Proof of identity",
            "Proof of Social Security Number",
            "Proof of Florida residential address"
        ],
        "accepted_forms": ['drivers_license', 'state_id', 'building_permit']
    },
    "new_license": {
        "name": "Get First Driver's License",
        "description": "Apply for your first Florida driver's license",
        "documents": [
            "Proof of identity",
            "Proof of Social Security Number",
            "Proof of Florida residential address",
            "Certificate of completion from Traffic Law course",
            "Passing test scores"
        ],
        "accepted_forms": ['state_id', 'building_permit']
    },
    "register_vehicle": {
        "name": "Register a Vehicle",
        "description": "Register a new or used vehicle in Florida",
        "documents": [
            "Proof of ownership",
            "Proof of Florida insurance",
            "Valid Florida driver's license",
            "VIN verification",
            "Application form HSMV 82040"
        ],
        "accepted_forms": ['vehicle_title', 'vehicle_registration', 'drivers_license']
    },
    "transfer_title": {
        "name": "Transfer Vehicle Title",
        "description": "Transfer ownership of a vehicle",
        "documents": [
            "Current vehicle title",
            "Valid Florida driver's license",
            "Proof of Florida insurance",
            "Odometer disclosure",
            "Bill of sale"
        ],
        "accepted_forms": ['vehicle_title', 'drivers_license', 'vehicle_registration']
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
    max-height: 400px;
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

.document-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border-left: 4px solid #e5e7eb;
}

.document-verified {
    border-left-color: #10b981;
    background: #f0fdf4;
}

.document-pending {
    border-left-color: #f59e0b;
    background: #fffbeb;
}

.upload-area {
    background: white;
    border: 2px dashed #cbd5e1;
    border-radius: 15px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
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

.detection-result {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}

.confidence-bar {
    background: #e5e7eb;
    height: 20px;
    border-radius: 10px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.confidence-fill {
    background: linear-gradient(90deg, #10b981, #34d399);
    height: 100%;
    transition: width 0.3s;
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
        "content": "👋 Welcome to the Florida DMV AI Assistant! I'm here to help you prepare for your DMV visit.\n\nWhat brings you to the DMV today?\n\n1. 🚗 **Renew Driver's License**\n2. 🆕 **Get First Driver's License**\n3. 📋 **Register a Vehicle**\n4. 📄 **Transfer Vehicle Title**"
    })

if 'selected_service' not in st.session_state:
    st.session_state.selected_service = None

if 'verified_documents' not in st.session_state:
    st.session_state.verified_documents = {}

if 'current_step' not in st.session_state:
    st.session_state.current_step = 'service_selection'

if 'classifier' not in st.session_state:
    st.session_state.classifier = FormClassifier()
    with st.spinner("🔧 Initializing AI model..."):
        try:
            st.session_state.classifier.quick_train()
        except:
            # If training fails, create empty model
            st.session_state.classifier.build_model()

if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = {}

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
        
        Be friendly, clear, and concise. Guide users through document verification."""
        
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
        return f"I'm here to help! Please select from the options above or tell me what DMV service you need."

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

def verify_document_with_ai(uploaded_file, required_documents, service_key):
    """Use the CNN model to classify the uploaded document"""
    try:
        # Read the uploaded file
        image = Image.open(uploaded_file)
        
        # Get prediction from model
        prediction = st.session_state.classifier.predict_form(image)
        
        if prediction:
            form_type = prediction['form_type']
            confidence = prediction['confidence']
            
            # Check if this form type is accepted for the service
            accepted_forms = DMV_SERVICES[service_key].get('accepted_forms', [])
            
            # Check what documents this form can satisfy
            satisfied_docs = []
            if form_type in FORM_TO_DOCUMENT_MAP:
                potential_docs = FORM_TO_DOCUMENT_MAP[form_type]
                for doc in potential_docs:
                    # Check if this document is in the required list
                    for req_doc in required_documents:
                        if doc.lower() in req_doc.lower() or req_doc.lower() in doc.lower():
                            satisfied_docs.append(req_doc)
            
            return {
                'detected_type': form_type,
                'confidence': confidence,
                'satisfied_documents': satisfied_docs,
                'is_accepted': form_type in accepted_forms,
                'probabilities': prediction['probabilities']
            }
    except Exception as e:
        return {
            'error': str(e),
            'detected_type': 'unknown',
            'confidence': 0,
            'satisfied_documents': [],
            'is_accepted': False
        }
    
    return None

# =====================================================
# MAIN APP INTERFACE
# =====================================================

# Header
st.markdown("""
<div class="main-header">
    <h1 style="color: #1f2937; margin: 0;">🚗 Florida DMV AI Assistant</h1>
    <p style="color: #6b7280; margin-top: 0.5rem;">Chat + Document Verification System</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📄 Document Upload", "✅ Verification Status"])

# =====================================================
# TAB 1: CHAT ASSISTANT
# =====================================================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Chat with DMV Assistant")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ai-message">🤖 {message["content"]}</div>', 
                              unsafe_allow_html=True)
        
        # User input
        user_input = st.text_input("Type your message...", 
                                  placeholder="E.g., 'I need to renew my driver's license'",
                                  key="chat_input")
        
        if st.button("Send", key="send_chat"):
            if user_input:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Process based on current step
                if st.session_state.current_step == 'service_selection':
                    service = identify_service_from_message(user_input)
                    
                    if service:
                        st.session_state.selected_service = service
                        st.session_state.current_step = 'document_collection'
                        service_info = DMV_SERVICES[service]
                        
                        response = f"Great! You want to **{service_info['name']}**.\n\n"
                        response += "📋 **Required Documents:**\n\n"
                        for i, doc in enumerate(service_info['documents'], 1):
                            response += f"{i}. {doc}\n"
                        response += "\n📤 **Please go to the 'Document Upload' tab to upload your documents.**"
                        
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        ai_response = get_ai_response(user_input, "User is selecting a DMV service")
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                elif st.session_state.current_step == 'document_collection':
                    # Check if all documents are verified
                    required_docs = DMV_SERVICES[st.session_state.selected_service]['documents']
                    all_verified = all(doc in st.session_state.verified_documents 
                                     for doc in required_docs)
                    
                    if all_verified:
                        response = """🎉 **Excellent! All documents verified!**
                        
✅ All required documents have been successfully uploaded and verified
✅ Ready for your DMV visit

**Next Steps:**
1. 📅 **Book Your Appointment**: Visit the DMV Portal
2. 🕐 **Arrive Early**: Get there 15 minutes before your scheduled time
3. 💳 **Bring Payment**: Have cash, check, or card ready

You're all set! Is there anything else you'd like to know?"""
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        missing_docs = [doc for doc in required_docs 
                                      if doc not in st.session_state.verified_documents]
                        response = f"You still need to upload: {', '.join(missing_docs)}\n\nPlease use the Document Upload tab."
                        st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.rerun()
    
    with col2:
        st.subheader("📊 Current Status")
        
        if st.session_state.selected_service:
            service_info = DMV_SERVICES[st.session_state.selected_service]
            st.info(f"**Service:** {service_info['name']}")
            
            required_docs = service_info['documents']
            verified_count = sum(1 for doc in required_docs 
                               if doc in st.session_state.verified_documents)
            
            st.progress(verified_count / len(required_docs))
            st.caption(f"{verified_count}/{len(required_docs)} documents verified")
        else:
            st.info("💡 Select a service to begin")

# =====================================================
# TAB 2: DOCUMENT UPLOAD
# =====================================================
with tab2:
    if st.session_state.selected_service:
        service_info = DMV_SERVICES[st.session_state.selected_service]
        
        st.subheader(f"📤 Upload Documents for {service_info['name']}")
        
        # Show required documents
        st.markdown("### Required Documents:")
        for doc in service_info['documents']:
            if doc in st.session_state.verified_documents:
                st.success(f"✅ {doc} - Verified")
            else:
                st.warning(f"⏳ {doc} - Pending")
        
        # Upload area
        st.markdown("---")
        st.markdown("### Upload Your Documents")
        
        uploaded_file = st.file_uploader(
            "Choose a document image",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Upload clear photos or scans of your documents"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📄 Uploaded Document")
                
                # Display the uploaded image
                if uploaded_file.type != 'application/pdf':
                    image = Image.open(uploaded_file)
                    st.image(image, use_column_width=True)
                else:
                    st.info("PDF uploaded - processing...")
            
            with col2:
                st.markdown("#### 🤖 AI Detection Results")
                
                # Process with AI
                with st.spinner("🔍 Analyzing document..."):
                    result = verify_document_with_ai(
                        uploaded_file, 
                        service_info['documents'],
                        st.session_state.selected_service
                    )
                
                if result and not result.get('error'):
                    # Show detection results
                    detected_type = result['detected_type']
                    confidence = result['confidence']
                    
                    # Display form type with friendly name
                    form_display_names = {
                        'drivers_license': "Driver's License",
                        'vehicle_registration': "Vehicle Registration",
                        'vehicle_title': "Vehicle Title",
                        'building_permit': "Building Permit",
                        'state_id': "State ID"
                    }
                    
                    st.metric("Detected Document", 
                            form_display_names.get(detected_type, detected_type.title()))
                    
                    # Confidence bar
                    st.progress(confidence)
                    st.caption(f"Confidence: {confidence*100:.1f}%")
                    
                    # Check if document satisfies requirements
                    if result['satisfied_documents']:
                        st.success(f"✅ This document satisfies: {', '.join(result['satisfied_documents'])}")
                        
                        # Add to verified documents
                        for doc in result['satisfied_documents']:
                            if doc not in st.session_state.verified_documents:
                                st.session_state.verified_documents[doc] = {
                                    'file_name': uploaded_file.name,
                                    'detected_type': detected_type,
                                    'confidence': confidence,
                                    'timestamp': datetime.now()
                                }
                        
                        st.balloons()
                        
                        # Check if all documents are now verified
                        all_verified = all(doc in st.session_state.verified_documents 
                                         for doc in service_info['documents'])
                        if all_verified:
                            st.success("🎉 All documents verified! You're ready for your DMV visit!")
                    else:
                        st.warning("⚠️ This document doesn't match any required documents for this service.")
                        st.info("Please upload one of the required documents listed above.")
                    
                    # Show probabilities
                    with st.expander("View Detection Details"):
                        for form, prob in result['probabilities'].items():
                            display_name = form_display_names.get(form, form.title())
                            st.write(f"{display_name}: {prob*100:.1f}%")
                else:
                    st.error("Could not process the document. Please try again with a clearer image.")
        
        # Option to generate sample documents for testing
        st.markdown("---")
        with st.expander("🧪 Generate Sample Documents for Testing"):
            st.info("Generate synthetic documents to test the AI detection system")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Generate License", key="gen_license"):
                    img_array = st.session_state.classifier.create_distinctive_form('drivers_license')
                    img = Image.fromarray(img_array.astype('uint8'))
                    st.image(img, caption="Sample Driver's License")
            
            with col2:
                if st.button("Generate Registration", key="gen_reg"):
                    img_array = st.session_state.classifier.create_distinctive_form('vehicle_registration')
                    img = Image.fromarray(img_array.astype('uint8'))
                    st.image(img, caption="Sample Registration")
            
            with col3:
                if st.button("Generate Title", key="gen_title"):
                    img_array = st.session_state.classifier.create_distinctive_form('vehicle_title')
                    img = Image.fromarray(img_array.astype('uint8'))
                    st.image(img, caption="Sample Title")
    
    else:
        st.info("💡 Please select a service in the Chat Assistant tab first")

# =====================================================
# TAB 3: VERIFICATION STATUS
# =====================================================
with tab3:
    st.subheader("✅ Document Verification Status")
    
    if st.session_state.selected_service:
        service_info = DMV_SERVICES[st.session_state.selected_service]
        
        st.markdown(f"### Service: {service_info['name']}")
        
        # Progress overview
        required_docs = service_info['documents']
        verified_count = sum(1 for doc in required_docs 
                           if doc in st.session_state.verified_documents)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Required", len(required_docs))
        with col2:
            st.metric("Verified", verified_count)
        with col3:
            st.metric("Remaining", len(required_docs) - verified_count)
        
        # Progress bar
        progress = verified_count / len(required_docs)
        st.progress(progress)
        
        if progress == 1.0:
            st.success("🎉 All documents verified! You're ready to book your appointment!")
            st.markdown("[**Book DMV Appointment →**](https://mydmvportal.flhsmv.gov/)")
        
        # Detailed status for each document
        st.markdown("### Document Checklist")
        
        for doc in required_docs:
            if doc in st.session_state.verified_documents:
                verified_info = st.session_state.verified_documents[doc]
                
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"✅ **{doc}**")
                    with col2:
                        st.caption(f"File: {verified_info['file_name']}")
                    with col3:
                        st.caption(f"Confidence: {verified_info['confidence']*100:.0f}%")
                    
                    form_display_names = {
                        'drivers_license': "Driver's License",
                        'vehicle_registration': "Vehicle Registration",
                        'vehicle_title': "Vehicle Title",
                        'building_permit': "Building Permit",
                        'state_id': "State ID"
                    }
                    detected_display = form_display_names.get(verified_info['detected_type'], 
                                                             verified_info['detected_type'])
                    st.caption(f"Detected as: {detected_display}")
                    st.markdown("---")
            else:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"⏳ **{doc}**")
                    with col2:
                        st.caption("Not uploaded")
                    st.caption("Please upload this document in the Document Upload tab")
                    st.markdown("---")
        
        # Reset button
        if st.button("🔄 Start Over", key="reset_verification"):
            st.session_state.verified_documents = {}
            st.session_state.selected_service = None
            st.session_state.current_step = 'service_selection'
            st.session_state.messages = [{
                "role": "assistant",
                "content": "👋 Welcome to the Florida DMV AI Assistant! I'm here to help you prepare for your DMV visit.\n\nWhat brings you to the DMV today?\n\n1. 🚗 **Renew Driver's License**\n2. 🆕 **Get First Driver's License**\n3. 📋 **Register a Vehicle**\n4. 📄 **Transfer Vehicle Title**"
            }]
            st.rerun()
    else:
        st.info("💡 Please select a service in the Chat Assistant tab to begin document verification")
        
        # Show a demo of what the system can detect
        st.markdown("### 🤖 Our AI Can Detect These Document Types:")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown("**Driver's License**")
            img_array = st.session_state.classifier.create_distinctive_form('drivers_license', seed=42)
            img = Image.fromarray(img_array.astype('uint8'))
            st.image(img, use_column_width=True)
        
        with col2:
            st.markdown("**Vehicle Registration**")
            img_array = st.session_state.classifier.create_distinctive_form('vehicle_registration', seed=42)
            img = Image.fromarray(img_array.astype('uint8'))
            st.image(img, use_column_width=True)
        
        with col3:
            st.markdown("**Vehicle Title**")
            img_array = st.session_state.classifier.create_distinctive_form('vehicle_title', seed=42)
            img = Image.fromarray(img_array.astype('uint8'))
            st.image(img, use_column_width=True)
        
        with col4:
            st.markdown("**Building Permit**")
            img_array = st.session_state.classifier.create_distinctive_form('building_permit', seed=42)
            img = Image.fromarray(img_array.astype('uint8'))
            st.image(img, use_column_width=True)
        
        with col5:
            st.markdown("**State ID**")
            img_array = st.session_state.classifier.create_distinctive_form('state_id', seed=42)
            img = Image.fromarray(img_array.astype('uint8'))
            st.image(img, use_column_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
    <p>🏛️ Florida Department of Highway Safety and Motor Vehicles</p>
    <p>AI Assistant with CNN Document Classification & OpenAI Chat</p>
    <p>CAP 4630 - Intro to Artificial Intelligence | Final Project</p>
</div>
""", unsafe_allow_html=True)
