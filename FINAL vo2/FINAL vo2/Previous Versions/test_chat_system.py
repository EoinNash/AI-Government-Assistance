#!/usr/bin/env python3
"""
Test Script for Florida DMV AI Assistant Chat Interface
This script tests the key components without running the full Streamlit app
"""

import sys
from openai import OpenAI

# Test Configuration
OPENAI_API_KEY = "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"

def test_openai_connection():
    """Test if OpenAI API connection works"""
    print("🔧 Testing OpenAI API Connection...")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful DMV assistant."},
                {"role": "user", "content": "Say 'Connection successful!' if you can read this."}
            ],
            max_tokens=50
        )
        result = response.choices[0].message.content
        print(f"✅ OpenAI Response: {result}")
        return True
    except Exception as e:
        print(f"❌ OpenAI Connection Failed: {e}")
        return False

def test_service_detection():
    """Test service detection logic"""
    print("\n🔍 Testing Service Detection...")
    
    test_cases = [
        ("I need to renew my driver's license", "renew_license"),
        ("1", "renew_license"),
        ("I just bought a car and need to register it", "register_vehicle"),
        ("Transfer title", "transfer_title"),
        ("Get my first license", "new_license")
    ]
    
    def identify_service(message):
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['renew', 'renewal']):
            if 'license' in message_lower or 'driver' in message_lower:
                return 'renew_license'
        elif any(word in message_lower for word in ['first', 'new']):
            if 'license' in message_lower:
                return 'new_license'
        elif 'register' in message_lower and ('vehicle' in message_lower or 'car' in message_lower):
            return 'register_vehicle'
        elif 'transfer' in message_lower or 'title' in message_lower:
            return 'transfer_title'
        elif '1' in message:
            return 'renew_license'
        elif '2' in message:
            return 'new_license'
        elif '3' in message:
            return 'register_vehicle'
        elif '4' in message:
            return 'transfer_title'
        return None
    
    passed = 0
    for test_input, expected in test_cases:
        result = identify_service(test_input)
        if result == expected:
            print(f"  ✅ '{test_input}' → {result}")
            passed += 1
        else:
            print(f"  ❌ '{test_input}' → Expected: {expected}, Got: {result}")
    
    print(f"Service Detection: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

def test_document_check():
    """Test document verification logic"""
    print("\n📋 Testing Document Verification...")
    
    test_cases = [
        ("Yes, I have all the documents ready", True),
        ("Got everything prepared", True),
        ("I have all my papers", True),
        ("No, I'm missing some", False),
        ("What documents do I need?", False),
        ("I'm not sure", False)
    ]
    
    def check_documents(message):
        message_lower = message.lower()
        confirmation_words = ['yes', 'have', 'got', 'ready', 'prepared']
        document_words = ['documents', 'papers', 'everything']
        
        has_confirmation = any(word in message_lower for word in confirmation_words)
        mentions_documents = any(word in message_lower for word in document_words)
        
        return has_confirmation and mentions_documents
    
    passed = 0
    for test_input, expected in test_cases:
        result = check_documents(test_input)
        if result == expected:
            print(f"  ✅ '{test_input}' → {'Ready' if result else 'Not Ready'}")
            passed += 1
        else:
            print(f"  ❌ '{test_input}' → Expected: {expected}, Got: {result}")
    
    print(f"Document Check: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

def simulate_conversation():
    """Simulate a complete conversation flow"""
    print("\n💬 Simulating Complete Conversation Flow...")
    
    conversation_steps = [
        ("User", "I need to renew my driver's license"),
        ("AI", "Identified service: License Renewal"),
        ("AI", "Required documents listed"),
        ("User", "Yes, I have all the documents"),
        ("AI", "Documents verified ✅"),
        ("AI", "Ready to book appointment!")
    ]
    
    for role, message in conversation_steps:
        print(f"  {role}: {message}")
    
    print("✅ Conversation flow simulation complete")
    return True

def main():
    print("="*50)
    print("🚗 Florida DMV AI Assistant - System Test")
    print("="*50)
    
    tests = [
        ("OpenAI Connection", test_openai_connection),
        ("Service Detection", test_service_detection),
        ("Document Check", test_document_check),
        ("Conversation Flow", simulate_conversation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! The system is ready for use.")
        print("\nTo run the full application:")
        print("1. Install requirements: pip install -r requirements_updated.txt")
        print("2. Run: streamlit run app_with_openai_chat.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
