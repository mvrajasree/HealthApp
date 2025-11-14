from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load ML models
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

try:
    with open(os.path.join(MODELS_DIR, 'emergency_level_model.pkl'), 'rb') as f:
        emergency_model = pickle.load(f)
    logger.info("Emergency level model loaded successfully")
except Exception as e:
    logger.error(f"Error loading emergency level model: {e}")
    emergency_model = None

try:
    with open(os.path.join(MODELS_DIR, 'recommended_specialty_model.pkl'), 'rb') as f:
        specialty_model = pickle.load(f)
    logger.info("Specialty recommendation model loaded successfully")
except Exception as e:
    logger.error(f"Error loading specialty model: {e}")
    specialty_model = None

try:
    with open(os.path.join(MODELS_DIR, 'wait_time_model.pkl'), 'rb') as f:
        wait_time_model = pickle.load(f)
    logger.info("Wait time model loaded successfully")
except Exception as e:
    logger.error(f"Error loading wait time model: {e}")
    wait_time_model = None

# In-memory storage for verification codes (use Redis in production)
verification_codes = {}

# Sample medical facilities database
MEDICAL_FACILITIES = [
    {"name": "City General Hospital", "type": "hospital", "latitude": 40.7128, "longitude": -74.0060, "wait_time": 45},
    {"name": "Downtown Medical Center", "type": "hospital", "latitude": 40.7589, "longitude": -73.9851, "wait_time": 30},
    {"name": "Community Urgent Care", "type": "urgent_care", "latitude": 40.7505, "longitude": -73.9934, "wait_time": 15},
    {"name": "Westside Clinic", "type": "clinic", "latitude": 40.7829, "longitude": -73.9654, "wait_time": 10},
    {"name": "Emergency Trauma Center", "type": "hospital", "latitude": 40.6413, "longitude": -73.7781, "wait_time": 60}
]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    models_status = {
        'emergency_model_loaded': emergency_model is not None,
        'specialty_model_loaded': specialty_model is not None,
        'wait_time_model_loaded': wait_time_model is not None
    }
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models': models_status
    })

@app.route('/api/send-verification', methods=['POST'])
def send_verification_code():
    """Send verification code to email or phone"""
    try:
        data = request.get_json()
        method = data.get('method')
        contact = data.get('contact')
        patient_id = data.get('patientId')
        
        # Generate random 6-digit code
        code = ''.join([str(np.random.randint(0, 9)) for _ in range(6)])
        
        # Store code with expiration (10 minutes)
        verification_codes[contact] = {
            'code': code,
            'expires': datetime.now() + timedelta(minutes=10),
            'patient_id': patient_id
        }
        
        logger.info(f"Verification code {code} sent to {contact} via {method}")
        
        # In production, integrate with email/SMS service here
        # For demo, we'll just log it
        if method == 'email':
            # Integrate with email service (SendGrid, SES, etc.)
            pass
        else:  # phone
            # Integrate with SMS service (Twilio, etc.)
            pass
            
        return jsonify({
            'success': True,
            'message': f'Verification code sent to your {method}',
            # For demo purposes, return the code (remove in production)
            'demo_code': code
        })
        
    except Exception as e:
        logger.error(f"Error sending verification code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    """Verify the provided code"""
    try:
        data = request.get_json()
        code = data.get('code')
        contact = data.get('contact')
        method = data.get('method')
        
        stored_data = verification_codes.get(contact)
        
        if not stored_data:
            return jsonify({'verified': False, 'error': 'No verification code found'})
        
        if datetime.now() > stored_data['expires']:
            del verification_codes[contact]
            return jsonify({'verified': False, 'error': 'Verification code expired'})
        
        if stored_data['code'] == code:
            del verification_codes[contact]
            return jsonify({'verified': True, 'message': 'Verification successful'})
        else:
            return jsonify({'verified': False, 'error': 'Invalid verification code'})
            
    except Exception as e:
        logger.error(f"Error verifying code: {e}")
        return jsonify({'verified': False, 'error': str(e)}), 500

@app.route('/api/analyze-symptoms', methods=['POST'])
def analyze_symptoms():
    """Analyze symptoms using ML models and return triage assessment"""
    try:
        patient_data = request.get_json()
        logger.info(f"Analyzing symptoms for patient: {patient_data.get('name', 'Unknown')}")
        
        # Prepare features for ML models
        features = prepare_features(patient_data)
        
        # Get predictions from ML models
        results = get_ml_predictions(features, patient_data)
        
        logger.info(f"Assessment results: {results}")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error analyzing symptoms: {e}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

def prepare_features(patient_data):
    """Prepare features for ML model inference"""
    # Map symptoms to numerical features
    symptom_mapping = {
        'chest_pain': 0, 'difficulty_breathing': 1, 'severe_bleeding': 2,
        'head_injury': 3, 'fever': 4, 'abdominal_pain': 5,
        'allergic_reaction': 6, 'stroke_symptoms': 7, 'burn': 8,
        'fracture': 9, 'headache': 10, 'rash': 11,
        'cough': 12, 'nausea': 13, 'dizziness': 14
    }
    
    # Create feature vector
    features = {
        'age': patient_data.get('age', 30),
        'symptom_encoded': symptom_mapping.get(patient_data.get('symptoms'), -1),
        'has_location_consent': 1 if patient_data.get('locationConsent') else 0,
        'hour_of_day': datetime.now().hour,
        'is_weekend': 1 if datetime.now().weekday() >= 5 else 0
    }
    
    return features

def get_ml_predictions(features, patient_data):
    """Get predictions from all ML models"""
    results = {}
    
    # Emergency level prediction
    if emergency_model:
        try:
            # Prepare input for emergency model
            emergency_input = prepare_model_input(features, emergency_model)
            emergency_pred = emergency_model.predict(emergency_input)[0]
            emergency_proba = emergency_model.predict_proba(emergency_input)[0]
            
            # Map prediction to emergency levels
            emergency_levels = ['LOW', 'MEDIUM', 'HIGH']
            results['emergencyLevel'] = emergency_levels[emergency_pred]
            results['confidence'] = float(max(emergency_proba))
            
        except Exception as e:
            logger.error(f"Emergency model prediction failed: {e}")
            results['emergencyLevel'] = fallback_emergency_level(patient_data)
            results['confidence'] = 0.5
    else:
        results['emergencyLevel'] = fallback_emergency_level(patient_data)
        results['confidence'] = 0.5
    
    # Specialty recommendation
    if specialty_model:
        try:
            specialty_input = prepare_model_input(features, specialty_model)
            specialty_pred = specialty_model.predict(specialty_input)[0]
            specialties = ['General Practitioner', 'Cardiologist', 'Pulmonologist', 
                          'Neurologist', 'Gastroenterologist', 'Dermatologist', 
                          'Orthopedist', 'Allergist', 'Emergency Physician']
            results['recommendedDoctor'] = specialties[min(specialty_pred, len(specialties)-1)]
        except Exception as e:
            logger.error(f"Specialty model prediction failed: {e}")
            results['recommendedDoctor'] = fallback_specialty(patient_data)
    else:
        results['recommendedDoctor'] = fallback_specialty(patient_data)
    
    # Wait time prediction
    if wait_time_model:
        try:
            wait_input = prepare_model_input(features, wait_time_model)
            wait_pred = wait_time_model.predict(wait_input)[0]
            results['appointmentTime'] = format_wait_time(wait_pred)
        except Exception as e:
            logger.error(f"Wait time model prediction failed: {e}")
            results['appointmentTime'] = fallback_appointment_time(results['emergencyLevel'])
    else:
        results['appointmentTime'] = fallback_appointment_time(results['emergencyLevel'])
    
    # Add additional result fields
    results.update({
        'emergencyClass': f'emergency-{results["emergencyLevel"].lower()}',
        'badgeClass': f'badge-{results["emergencyLevel"].lower()}',
        'urgencyText': get_urgency_text(results['emergencyLevel']),
        'timestamp': datetime.now().isoformat()
    })
    
    return results

def prepare_model_input(features, model):
    """Prepare input data for model prediction"""
    # This is a simplified version - adjust based on your model's expected input
    if hasattr(model, 'feature_names_in_'):
        # Create input with correct feature order
        input_data = []
        for feature_name in model.feature_names_in_:
            input_data.append(features.get(feature_name, 0))
        return np.array([input_data])
    else:
        # Fallback for models without feature names
        input_data = [features['age'], features['symptom_encoded'], 
                     features['has_location_consent'], features['hour_of_day']]
        return np.array([input_data])

def fallback_emergency_level(patient_data):
    """Fallback emergency level determination"""
    high_emergency_symptoms = ['chest_pain', 'difficulty_breathing', 'severe_bleeding', 
                              'head_injury', 'allergic_reaction', 'stroke_symptoms']
    
    symptom = patient_data.get('symptoms')
    age = patient_data.get('age', 30)
    
    if symptom in high_emergency_symptoms:
        return 'HIGH'
    elif symptom in ['fever', 'abdominal_pain', 'fracture']:
        return 'MEDIUM'
    else:
        return 'LOW'

def fallback_specialty(patient_data):
    """Fallback specialty recommendation"""
    symptom_specialty_map = {
        'chest_pain': 'Cardiologist',
        'difficulty_breathing': 'Pulmonologist',
        'head_injury': 'Neurologist',
        'abdominal_pain': 'Gastroenterologist',
        'fracture': 'Orthopedist',
        'allergic_reaction': 'Allergist',
        'burn': 'Dermatologist',
        'rash': 'Dermatologist'
    }
    
    return symptom_specialty_map.get(patient_data.get('symptoms'), 'General Practitioner')

def fallback_appointment_time(emergency_level):
    """Fallback appointment time based on emergency level"""
    if emergency_level == 'HIGH':
        return 'Immediate - Emergency Room'
    elif emergency_level == 'MEDIUM':
        return 'Today - Urgent Care'
    else:
        return 'Within 2-3 days'

def format_wait_time(minutes):
    """Format wait time in minutes to human readable"""
    if minutes < 60:
        return f'Within {int(minutes)} minutes'
    elif minutes < 120:
        return f'Within {int(minutes/60)} hour'
    else:
        return f'Within {int(minutes/60)} hours'

def get_urgency_text(emergency_level):
    """Get urgency text based on emergency level"""
    urgency_texts = {
        'HIGH': 'URGENT - SEEK IMMEDIATE CARE',
        'MEDIUM': 'SEEK CARE TODAY',
        'LOW': 'SCHEDULE APPOINTMENT'
    }
    return urgency_texts.get(emergency_level, 'CONSULT HEALTHCARE PROVIDER')

@app.route('/api/nearby-facilities', methods=['POST'])
def find_nearby_facilities():
    """Find nearby medical facilities based on location"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 10)  # miles
        
        logger.info(f"Finding facilities near {latitude}, {longitude}")
        
        # Calculate distances and sort facilities
        facilities_with_distance = []
        for facility in MEDICAL_FACILITIES:
            distance = calculate_distance(
                latitude, longitude,
                facility['latitude'], facility['longitude']
            )
            if distance <= radius:
                facilities_with_distance.append({
                    **facility,
                    'distance': round(distance, 1),
                    'distance_units': 'miles'
                })
        
        # Sort by distance
        facilities_with_distance.sort(key=lambda x: x['distance'])
        
        return jsonify({
            'facilities': facilities_with_distance[:5],  # Return top 5 closest
            'user_location': {'latitude': latitude, 'longitude': longitude}
        })
        
    except Exception as e:
        logger.error(f"Error finding facilities: {e}")
        return jsonify({'error': 'Failed to find facilities', 'details': str(e)}), 500

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in miles"""
    # Haversine formula
    R = 3958.8  # Earth radius in miles
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c

@app.route('/api/log-assessment', methods=['POST'])
def log_assessment():
    """Log assessment data for analytics"""
    try:
        data = request.get_json()
        logger.info(f"Assessment logged: {data.get('patientData', {}).get('name', 'Unknown')}")
        
        # In production, store in database
        # For demo, just log the assessment
        assessment_data = {
            'timestamp': datetime.now().isoformat(),
            'patient_data': data.get('patientData', {}),
            'results': data.get('results', {}),
            'log_id': f"LOG{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        return jsonify({'success': True, 'log_id': assessment_data['log_id']})
        
    except Exception as e:
        logger.error(f"Error logging assessment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/resend-code', methods=['POST'])
def resend_code():
    """Resend verification code"""
    try:
        data = request.get_json()
        method = data.get('method')
        contact = data.get('contact')
        
        # Generate new code
        code = ''.join([str(np.random.randint(0, 9)) for _ in range(6)])
        
        # Update stored code
        verification_codes[contact] = {
            'code': code,
            'expires': datetime.now() + timedelta(minutes=10)
        }
        
        logger.info(f"New verification code {code} sent to {contact}")
        
        return jsonify({
            'success': True,
            'message': f'New verification code sent to your {method}',
            'demo_code': code  # Remove in production
        })
        
    except Exception as e:
        logger.error(f"Error resending code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
