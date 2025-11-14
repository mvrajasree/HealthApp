#!/usr/bin/env python3
"""
Production runner for Medical Triage API
"""

from app import app

if __name__ == '__main__':
    print("Starting Medical Triage API Server...")
    print("Models loaded:")
    print(f"  - Emergency Level Model: {'Loaded' if app.emergency_model else 'Failed'}")
    print(f"  - Specialty Model: {'Loaded' if app.specialty_model else 'Failed'}")
    print(f"  - Wait Time Model: {'Loaded' if app.wait_time_model else 'Failed'}")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
