#!/usr/bin/env python3
"""
Quick Test Script for Document Verification Feature
Run this to test the CNN model's document detection capabilities
"""

import numpy as np
from PIL import Image, ImageDraw
import io

def create_test_documents():
    """Create sample documents for testing"""
    
    print("🎨 Generating Test Documents...")
    print("-" * 50)
    
    documents = {}
    
    # Create Driver's License
    img = Image.new('L', (128, 128), color=255)
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 50, 50], outline=0, width=2)  # Photo box
    for y in range(60, 120, 10):
        draw.line([10, y, 118, y], fill=0, width=1)  # Lines for text
    documents['drivers_license'] = img
    print("✅ Generated: Driver's License")
    
    # Create Vehicle Registration
    img = Image.new('L', (128, 128), color=255)
    draw = ImageDraw.Draw(img)
    for x in range(10, 120, 20):
        draw.line([x, 10, x, 118], fill=0, width=1)
    for y in range(10, 120, 20):
        draw.line([10, y, 118, y], fill=0, width=1)
    documents['vehicle_registration'] = img
    print("✅ Generated: Vehicle Registration")
    
    # Create Vehicle Title
    img = Image.new('L', (128, 128), color=255)
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 60, 60], outline=0, width=3)
    draw.rectangle([68, 10, 118, 60], outline=0, width=3)
    draw.line([10, 70, 118, 118], fill=0, width=3)
    documents['vehicle_title'] = img
    print("✅ Generated: Vehicle Title")
    
    # Create State ID
    img = Image.new('L', (128, 128), color=255)
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, 113, 113], outline=0, width=3)
    draw.ellipse([45, 45, 83, 83], outline=0, width=2)
    documents['state_id'] = img
    print("✅ Generated: State ID")
    
    # Create Building Permit
    img = Image.new('L', (128, 128), color=255)
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 118, 30], fill=0)  # Black header
    for x in range(20, 110, 15):
        draw.rectangle([x, 40, x+8, 118], fill=0)
    documents['building_permit'] = img
    print("✅ Generated: Building Permit")
    
    return documents

def save_test_documents():
    """Save test documents to files for upload testing"""
    
    documents = create_test_documents()
    
    print("\n📁 Saving Test Documents...")
    print("-" * 50)
    
    for doc_type, img in documents.items():
        filename = f"test_{doc_type}.png"
        img.save(filename)
        print(f"💾 Saved: {filename}")
    
    print("\n✅ All test documents saved!")
    print("\n" + "="*50)
    print("🎯 TESTING INSTRUCTIONS:")
    print("="*50)
    print("""
1. Run the main app:
   streamlit run app_complete_with_document_verification.py

2. In the Chat tab:
   - Type "1" to select license renewal
   - Or type "3" to register a vehicle

3. Go to Document Upload tab:
   - Upload test_drivers_license.png
   - Watch AI detect it with confidence %
   - See checkmark appear when verified!

4. Check Verification Status tab:
   - See progress bar fill up
   - View document checklist with ✅

5. Upload more test documents:
   - test_vehicle_registration.png
   - test_vehicle_title.png
   - test_state_id.png
   - test_building_permit.png

Watch as each document gets:
- 🔍 Detected by CNN model
- ✅ Verified against requirements  
- 📊 Added to progress tracker
""")

def test_document_matching():
    """Test the document matching logic"""
    
    print("\n🧪 Testing Document Matching Logic...")
    print("-" * 50)
    
    # Simulate document requirements for different services
    services = {
        "Renew License": ["Current driver's license", "Proof of identity", "Proof of address"],
        "Register Vehicle": ["Proof of ownership", "Vehicle registration", "Insurance"],
        "Transfer Title": ["Vehicle title", "Driver's license", "Bill of sale"]
    }
    
    # Simulate what each document type can satisfy
    document_mappings = {
        "drivers_license": ["Current driver's license", "Proof of identity", "Driver's license"],
        "vehicle_registration": ["Vehicle registration", "Insurance"],
        "vehicle_title": ["Vehicle title", "Proof of ownership"],
        "state_id": ["Proof of identity"],
        "building_permit": ["Proof of address"]
    }
    
    for service, requirements in services.items():
        print(f"\n📋 Service: {service}")
        print(f"   Required: {', '.join(requirements)}")
        
        for doc_type, satisfies in document_mappings.items():
            matched = [req for req in requirements if any(s in req or req in s for s in satisfies)]
            if matched:
                print(f"   ✅ {doc_type} → Satisfies: {', '.join(matched)}")

if __name__ == "__main__":
    print("="*50)
    print("🚗 DMV AI Document Verification - Test Generator")
    print("="*50)
    
    # Generate and save test documents
    save_test_documents()
    
    # Test matching logic
    test_document_matching()
    
    print("\n🎉 Test setup complete! Follow instructions above to test.")
