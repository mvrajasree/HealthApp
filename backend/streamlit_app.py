import streamlit as st
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

# Set page config
st.set_page_config(
    page_title="Secure Medical Triage System",
    page_icon="🏥",
    layout="wide"
)

# Load ML models
@st.cache_resource
def load_models():
    models = {}
    try:
        with open('backend/models/emergency_level_model.pkl', 'rb') as f:
            models['emergency'] = pickle.load(f)
        with open('backend/models/recommended_specialty_model.pkl', 'rb') as f:
            models['specialty'] = pickle.load(f)
        with open('backend/models/wait_time_model.pkl', 'rb') as f:
            models['wait_time'] = pickle.load(f)
        return models
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# Load models
models = load_models()

# Header
st.title("🏥 Secure Medical Triage System")
st.markdown("### Privacy-focused healthcare assessment with verification")

# Step 1: Patient Information
if st.session_state.current_step == 1:
    st.header("👤 Patient Information")
    
    with st.form("patient_info"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=1, max_value=120)
        
        with col2:
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
        
        symptoms = st.selectbox(
            "Primary Symptom",
            [
                "Select your primary symptom",
                "chest_pain", "difficulty_breathing", "severe_bleeding",
                "head_injury", "fever", "abdominal_pain",
                "allergic_reaction", "stroke_symptoms", "burn",
                "fracture", "headache", "rash",
                "cough", "nausea", "dizziness"
            ]
        )
        
        privacy_consent = st.checkbox(
            "I consent to the collection and processing of my personal and health data"
        )
        
        if st.form_submit_button("Continue to Verification"):
            if all([name, age, email, phone]) and symptoms != "Select your primary symptom" and privacy_consent:
                st.session_state.patient_data = {
                    'name': name, 'age': age, 'email': email, 
                    'phone': phone, 'symptoms': symptoms
                }
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please fill all required fields and provide consent")

# Step 2: Assessment Results
elif st.session_state.current_step == 2:
    st.header("📊 Triage Assessment Results")
    
    if models:
        # Prepare features for ML model
        features = {
            'age': st.session_state.patient_data['age'],
            'symptoms': st.session_state.patient_data['symptoms']
        }
        
        # Get predictions (simplified for demo)
        emergency_level = "HIGH" if features['symptoms'] in ['chest_pain', 'difficulty_breathing'] else "MEDIUM"
        
        # Display results
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Emergency Level", emergency_level)
        
        with col2:
            st.metric("Recommended Doctor", "General Practitioner")
        
        with col3:
            st.metric("Appointment Time", "Within 24 hours")
        
        with col4:
            st.metric("Facility", "Nearest Hospital")
    
    else:
        st.error("ML models not loaded properly")
    
    if st.button("Start New Assessment"):
        st.session_state.current_step = 1
        st.session_state.patient_data = {}
        st.rerun()

# Add some styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton button {
        background-color: #2c7fb8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
