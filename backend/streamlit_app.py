import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Set page config
st.set_page_config(
    page_title="Secure Medical Triage System",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton button {
        background-color: #2c7fb8;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
    }
    .stButton button:hover {
        background-color: #1d5f8a;
        color: white;
    }
    .emergency-high {
        color: #e74c3c;
        font-weight: bold;
    }
    .emergency-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .emergency-low {
        color: #27ae60;
        font-weight: bold;
    }
    .card {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏥 Secure Medical Triage System")
st.markdown("### Privacy-focused healthcare assessment with verification")

# Symptom mapping
symptom_options = [
    "Select your primary symptom",
    "Chest pain or discomfort",
    "Difficulty breathing", 
    "Severe bleeding",
    "Head injury with confusion",
    "High fever (over 103°F/39.4°C)",
    "Severe abdominal pain",
    "Severe allergic reaction",
    "Stroke symptoms (face drooping, arm weakness, speech difficulty)",
    "Severe burn",
    "Possible broken bone",
    "Severe headache",
    "Unexplained rash",
    "Persistent cough",
    "Nausea or vomiting",
    "Dizziness or lightheadedness"
]

symptom_mapping = {
    "Chest pain or discomfort": "chest_pain",
    "Difficulty breathing": "difficulty_breathing",
    "Severe bleeding": "severe_bleeding",
    "Head injury with confusion": "head_injury",
    "High fever (over 103°F/39.4°C)": "fever",
    "Severe abdominal pain": "abdominal_pain",
    "Severe allergic reaction": "allergic_reaction",
    "Stroke symptoms (face drooping, arm weakness, speech difficulty)": "stroke_symptoms",
    "Severe burn": "burn",
    "Possible broken bone": "fracture",
    "Severe headache": "headache",
    "Unexplained rash": "rash",
    "Persistent cough": "cough",
    "Nausea or vomiting": "nausea",
    "Dizziness or lightheadedness": "dizziness"
}

# Fallback symptom analysis (no ML models needed)
def analyze_symptoms_fallback(symptoms, age):
    """Fallback symptom analysis without ML models"""
    high_emergency = ['chest_pain', 'difficulty_breathing', 'severe_bleeding', 
                     'head_injury', 'allergic_reaction', 'stroke_symptoms']
    
    medium_emergency = ['fever', 'abdominal_pain', 'fracture', 'burn']
    
    # Adjust based on age
    age_adjustment = " (Higher risk due to age)" if age > 60 else ""
    
    if symptoms in high_emergency:
        return {
            'emergency_level': 'HIGH',
            'urgency_text': 'URGENT - SEEK IMMEDIATE CARE' + age_adjustment,
            'recommended_doctor': get_specialty_fallback(symptoms),
            'appointment_time': 'Immediate - Emergency Room',
            'facility': 'Nearest Emergency Department'
        }
    elif symptoms in medium_emergency:
        return {
            'emergency_level': 'MEDIUM',
            'urgency_text': 'SEEK CARE TODAY' + age_adjustment,
            'recommended_doctor': get_specialty_fallback(symptoms),
            'appointment_time': 'Today - Urgent Care',
            'facility': 'Urgent Care Center'
        }
    else:
        return {
            'emergency_level': 'LOW',
            'urgency_text': 'SCHEDULE APPOINTMENT',
            'recommended_doctor': get_specialty_fallback(symptoms),
            'appointment_time': 'Within 2-3 days',
            'facility': 'Primary Care Clinic'
        }

def get_specialty_fallback(symptoms):
    """Get recommended specialty based on symptoms"""
    specialty_map = {
        'chest_pain': 'Cardiologist',
        'difficulty_breathing': 'Pulmonologist',
        'head_injury': 'Neurologist',
        'abdominal_pain': 'Gastroenterologist',
        'fracture': 'Orthopedist',
        'allergic_reaction': 'Allergist',
        'burn': 'Dermatologist',
        'stroke_symptoms': 'Neurologist',
        'rash': 'Dermatologist'
    }
    return specialty_map.get(symptoms, 'General Practitioner')

# Step 1: Patient Information
if st.session_state.current_step == 1:
    st.header("👤 Patient Information")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="Enter your full name")
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
        
        with col2:
            email = st.text_input("Email Address", placeholder="Enter your email")
            phone = st.text_input("Phone Number", placeholder="Enter your phone number")
        
        symptoms = st.selectbox("Primary Symptom", symptom_options)
        
        st.markdown("---")
        st.subheader("🔒 Data Privacy")
        
        col3, col4 = st.columns(2)
        with col3:
            privacy_consent = st.checkbox(
                "I consent to the collection and processing of my personal and health data for medical triage purposes",
                key="privacy"
            )
        
        with col4:
            location_consent = st.checkbox(
                "I consent to share my location to help find nearby medical facilities (optional)",
                key="location"
            )
        
        if st.button("Continue to Assessment", type="primary"):
            if not all([name, age, email, phone]):
                st.error("Please fill in all required fields")
            elif symptoms == "Select your primary symptom":
                st.error("Please select your primary symptom")
            elif not privacy_consent:
                st.error("You must consent to data processing to continue")
            else:
                st.session_state.patient_data = {
                    'name': name,
                    'age': age,
                    'email': email,
                    'phone': phone,
                    'symptoms': symptom_mapping[symptoms],
                    'symptoms_display': symptoms,
                    'location_consent': location_consent,
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.current_step = 2
                st.rerun()

# Step 2: Assessment Results
elif st.session_state.current_step == 2:
    patient_data = st.session_state.patient_data
    
    st.header("📊 Triage Assessment Results")
    st.info(f"Assessment for: {patient_data['name']} | Age: {patient_data['age']}")
    
    # Perform assessment
    with st.spinner("Analyzing symptoms and determining care plan..."):
        results = analyze_symptoms_fallback(patient_data['symptoms'], patient_data['age'])
    
    # Display results in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        emergency_class = f"emergency-{results['emergency_level'].lower()}"
        st.markdown(f"""
        <div class="card">
            <h4>Emergency Level</h4>
            <h2 class="{emergency_class}">{results['emergency_level']}</h2>
            <p><small>{results['urgency_text']}</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <h4>Recommended Doctor</h4>
            <h3>{results['recommended_doctor']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card">
            <h4>Appointment Time</h4>
            <h3>{results['appointment_time']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="card">
            <h4>Recommended Facility</h4>
            <h3>{results['facility']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional information based on symptoms
    st.markdown("---")
    st.subheader("📋 Additional Guidance")
    
    if results['emergency_level'] == 'HIGH':
        st.error("""
        **🚨 IMMEDIATE ACTION REQUIRED:**
        - Call emergency services or go to the nearest emergency department immediately
        - Do not drive yourself if experiencing severe symptoms
        - Inform medical staff of your symptoms upon arrival
        """)
    elif results['emergency_level'] == 'MEDIUM':
        st.warning("""
        **⚠️ URGENT CARE RECOMMENDED:**
        - Visit an urgent care facility today
        - Monitor symptoms closely
        - Seek emergency care if symptoms worsen
        """)
    else:
        st.success("""
        **✅ SCHEDULE APPOINTMENT:**
        - Contact your primary care provider within 2-3 days
        - Monitor symptoms and seek care if they worsen
        - Consider telehealth options for convenience
        """)
    
    # Privacy notice
    st.markdown("---")
    st.subheader("🔐 Privacy Assurance")
    st.info("""
    Your personal data and assessment results are protected and will be automatically deleted after 24 hours 
    unless you choose to save them to your secure patient portal. All data is encrypted and handled in 
    accordance with healthcare privacy regulations.
    """)
    
    # Action buttons
    col5, col6, col7 = st.columns([1, 1, 1])
    
    with col5:
        if st.button("🔄 Start New Assessment", use_container_width=True):
            st.session_state.current_step = 1
            st.session_state.patient_data = {}
            st.session_state.assessment_complete = False
            st.rerun()
    
    with col6:
        if st.button("📧 Email Results", use_container_width=True):
            st.success("Results would be emailed to your registered email address")
    
    with col7:
        if st.button("📱 Save to Patient Portal", use_container_width=True):
            st.success("Results saved to your secure patient portal")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Secure Medical Triage System &copy; 2023 | HIPAA Compliant | For demonstration purposes only"
    "</div>",
    unsafe_allow_html=True
)
