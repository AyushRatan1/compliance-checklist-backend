#!/usr/bin/env python3
"""
Professional Compliance Checklist Generator API Test Suite
Tests AWS Bedrock Claude integration with various compliance scenarios
"""

import requests
import json
import time
import base64

# API endpoint
API_URL = "http://localhost:8000"

def print_header(title):
    print("\n" + "="*80)
    print(f"🧪 TEST: {title}")
    print("="*80)

def print_result(success, response_data=None, error=None):
    if success:
        print("✅ SUCCESS!")
        if response_data:
            checklists = response_data.get('checklists', [])
            metadata = response_data.get('metadata', {})
            
            print(f"\n📊 Generated {len(checklists)} checklists")
            if metadata:
                print(f"📂 Categories: {', '.join(metadata.get('categories', []))}")
                context = metadata.get('generation_context', {})
                if context:
                    print(f"🏢 Industry: {context.get('industry', 'Not specified')}")
                    print(f"🌍 Jurisdiction: {context.get('jurisdiction', 'Not specified')}")
            
            for i, checklist in enumerate(checklists[:2], 1):  # Show first 2
                print(f"\n📋 Checklist {i}: {checklist['checklist_name']}")
                print(f"📂 Category: {checklist['checklist_category']}")
                if checklist.get('priority'):
                    print(f"⚡ Priority: {checklist['priority']}")
                if checklist.get('frequency'):
                    print(f"📅 Frequency: {checklist['frequency']}")
                
                # Show first verification step
                desc = checklist['checklist_ai_description']
                first_step = desc.split('.')[0] if desc else "No description"
                print(f"🔍 First step: {first_step[:100]}...")
    else:
        print("❌ FAILED!")
        if error:
            print(f"Error: {error}")

# Test 1: Basic compliance text with industry context
print_header("Banking KYC/AML Compliance Requirements")
test_data_1 = {
    "primary_references": [
        """
        Banks must implement robust Know Your Customer (KYC) procedures including:
        - Customer identification with Officially Valid Documents (OVD)
        - Risk-based customer categorization (Low/Medium/High)
        - Beneficial ownership identification for corporate accounts
        - Enhanced Due Diligence for Politically Exposed Persons (PEPs)
        - Periodic KYC updates: High-risk every 2 years, Medium-risk every 8 years
        - Suspicious Transaction Report (STR) filing within 7 days
        - Cash Transaction Reports for transactions ≥ ₹10 lakh
        - FATCA/CRS compliance for tax residency reporting
        """
    ],
    "industry": "Banking & Financial Services",
    "jurisdiction": "India",
    "compliance_framework": "Basel III",
    "audience": "Compliance",
    "detail_level": "comprehensive"
}

try:
    response = requests.post(f"{API_URL}/generate-checklist", json=test_data_1, timeout=60)
    print_result(response.status_code == 200, response.json() if response.status_code == 200 else None, 
                response.text if response.status_code != 200 else None)
except Exception as e:
    print_result(False, error=str(e))

# Test 2: Healthcare HIPAA compliance with context hints
print_header("Healthcare HIPAA Privacy & Security")
test_data_2 = {
    "primary_references": [
        """
        HIPAA Security Rule requires covered entities to:
        - Implement administrative, physical, and technical safeguards
        - Conduct risk assessments and implement security measures
        - Assign security officer responsible for security policies
        - Implement access controls with unique user identification
        - Use encryption for electronic PHI transmission
        - Maintain audit logs of information system activity
        - Implement workforce training on security awareness
        - Have incident response procedures for security incidents
        """
    ],
    "context_scope_hints": "Focus specifically on technical safeguards and access controls for electronic health records systems",
    "industry": "Healthcare",
    "jurisdiction": "United States",
    "compliance_framework": "HIPAA",
    "audience": "IT Security Operations",
    "detail_level": "comprehensive"
}

try:
    response = requests.post(f"{API_URL}/generate-checklist", json=test_data_2, timeout=60)
    print_result(response.status_code == 200, response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None)
except Exception as e:
    print_result(False, error=str(e))

# Test 3: GDPR data protection with multiple references
print_header("GDPR Data Protection Multi-Source")
test_data_3 = {
    "primary_references": [
        """
        GDPR Article 32 - Security of processing:
        Taking into account the state of the art, the costs of implementation and the nature, scope, context and purposes of processing as well as the risk of varying likelihood and severity for the rights and freedoms of natural persons, the controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate:
        (a) the pseudonymisation and encryption of personal data;
        (b) the ability to ensure the ongoing confidentiality, integrity, availability and resilience of processing systems and services;
        """,
        """
        GDPR Article 33 - Notification of a personal data breach to the supervisory authority:
        In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of it, notify the personal data breach to the supervisory authority competent in accordance with Article 55, unless the personal data breach is unlikely to result in a risk to the rights and freedoms of natural persons.
        """
    ],
    "industry": "Technology",
    "jurisdiction": "European Union",
    "compliance_framework": "GDPR",
    "audience": "Legal",
    "detail_level": "comprehensive"
}

try:
    response = requests.post(f"{API_URL}/generate-checklist", json=test_data_3, timeout=60)
    print_result(response.status_code == 200, response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None)
except Exception as e:
    print_result(False, error=str(e))

# Test 4: API health check
print_header("Service Health Check")
try:
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        health_data = response.json()
        print("✅ Service is healthy!")
        print(f"🔧 Bedrock configured: {health_data.get('bedrock_configured', False)}")
        print(f"🤖 Model: {health_data.get('model', 'Not configured')}")
    else:
        print_result(False, error=f"Health check failed: {response.status_code}")
except Exception as e:
    print_result(False, error=str(e))

# Test 5: Supported formats check
print_header("Supported Formats & Options")
try:
    response = requests.get(f"{API_URL}/supported-formats")
    if response.status_code == 200:
        formats_data = response.json()
        print("✅ Formats retrieved successfully!")
        print(f"📁 Document formats: {', '.join(formats_data.get('document_formats', []))}")
        print(f"🏢 Industries: {len(formats_data.get('industries', []))} supported")
        print(f"🌍 Jurisdictions: {len(formats_data.get('jurisdictions', []))} supported")
        print(f"📋 Frameworks: {len(formats_data.get('frameworks', []))} supported")
    else:
        print_result(False, error=f"Formats check failed: {response.status_code}")
except Exception as e:
    print_result(False, error=str(e))

# Test 6: File upload simulation (base64 encoded text)
print_header("File Upload Simulation")
sample_text = """
SOC 2 Type II Control Requirements:
- Logical access controls must restrict system access to authorized users
- Multi-factor authentication required for all administrative access
- User access reviews must be performed quarterly
- Privileged access must be monitored and logged
- Password complexity requirements: minimum 12 characters
- Account lockout after 5 failed login attempts
- Session timeout after 30 minutes of inactivity
"""

# Encode as base64 (simulating file upload)
encoded_content = base64.b64encode(sample_text.encode()).decode()

test_data_6 = {
    "primary_references": [],
    "uploaded_files": [encoded_content],
    "file_names": ["soc2_requirements.txt"],
    "industry": "Technology",
    "jurisdiction": "United States",
    "compliance_framework": "SOC 2",
    "audience": "Internal Audit",
    "detail_level": "comprehensive"
}

try:
    response = requests.post(f"{API_URL}/generate-checklist", json=test_data_6, timeout=60)
    print_result(response.status_code == 200, response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None)
except Exception as e:
    print_result(False, error=str(e))

print("\n" + "="*80)
print("🎉 TEST SUITE COMPLETED")
print("="*80)
print("\n💡 Tips for testing:")
print("1. Ensure AWS Bedrock credentials are properly configured")
print("2. Verify Claude model access in your AWS region")
print("3. Check that the backend service is running on port 8000")
print("4. Monitor response times - comprehensive checklists may take 10-15 seconds")
print("\n🔗 Access the interactive UI at: http://localhost:5173")
print("📚 API Documentation: http://localhost:8000/docs") 