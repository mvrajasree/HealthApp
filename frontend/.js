// Main Application Controller
class MedicalTriageApp {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.patientData = {};
        this.verificationCode = '';
        
        this.initializeApp();
    }
    
    initializeApp() {
        this.bindEvents();
        this.generateVerificationCode();
        this.updateStepIndicator();
    }
    
    bindEvents() {
        // Step navigation
        document.getElementById('nextToVerification').addEventListener('click', () => this.validatePatientInfo());
        document.getElementById('backToPatientInfo').addEventListener('click', () => this.switchTab(1));
        document.getElementById('nextToLocation').addEventListener('click', () => this.switchTab(3));
        document.getElementById('backToVerification').addEventListener('click', () => this.switchTab(2));
        document.getElementById('nextToResults').addEventListener('click', () => this.processTriageAssessment());
        
        // Verification method change
        document.getElementById('verificationMethod').addEventListener('change', (e) => this.handleVerificationMethodChange(e));
        
        // Code input handling
        this.setupCodeInputs();
        
        // New assessment
        document.getElementById('newAssessment').addEventListener('click', () => this.resetApp());
        
        // Real-time validation
        this.setupRealTimeValidation();
    }
    
    setupRealTimeValidation() {
        const inputs = document.querySelectorAll('#patientForm input, #patientForm select');
        inputs.forEach(input => {
            input.addEventListener('blur', (e) => this.validateField(e.target));
            input.addEventListener('input', (e) => this.clearError(e.target));
        });
    }
    
    validateField(field) {
        const value = field.value.trim();
        const fieldId = field.id;
        
        this.clearError(field);
        
        switch(fieldId) {
            case 'patientName':
                if (!value) {
                    this.showError(field, 'Name is required');
                } else if (value.length < 2) {
                    this.showError(field, 'Name must be at least 2 characters');
                }
                break;
                
            case 'patientAge':
                if (!value) {
                    this.showError(field, 'Age is required');
                } else if (value < 1 || value > 120) {
                    this.showError(field, 'Please enter a valid age (1-120)');
                }
                break;
                
            case 'patientEmail':
                if (!value) {
                    this.showError(field, 'Email is required');
                } else if (!this.isValidEmail(value)) {
                    this.showError(field, 'Please enter a valid email address');
                }
                break;
                
            case 'patientPhone':
                if (!value) {
                    this.showError(field, 'Phone number is required');
                } else if (!this.isValidPhone(value)) {
                    this.showError(field, 'Please enter a valid phone number');
                }
                break;
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/\D/g, ''));
    }
    
    showError(field, message) {
        field.classList.add('error');
        const errorElement = document.getElementById(field.id + 'Error');
        if (errorElement) {
            errorElement.textContent = message;
        }
    }
    
    clearError(field) {
        field.classList.remove('error');
        const errorElement = document.getElementById(field.id + 'Error');
        if (errorElement) {
            errorElement.textContent = '';
        }
    }
    
    validatePatientInfo() {
        const requiredFields = ['patientName', 'patientAge', 'patientEmail', 'patientPhone', 'patientSymptoms'];
        let isValid = true;
        
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            this.validateField(field);
            if (field.classList.contains('error')) {
                isValid = false;
            }
        });
        
        const privacyConsent = document.getElementById('privacyConsent');
        if (!privacyConsent.checked) {
            this.showError(privacyConsent, 'You must consent to data processing to continue');
            isValid = false;
        }
        
        if (isValid) {
            this.savePatientData();
            this.switchTab(2);
        } else {
            this.scrollToFirstError();
        }
        
        return isValid;
    }
    
    scrollToFirstError() {
        const firstError = document.querySelector('.error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
    
    savePatientData() {
        this.patientData = {
            name: document.getElementById('patientName').value,
            age: document.getElementById('patientAge').value,
            email: document.getElementById('patientEmail').value,
            phone: document.getElementById('patientPhone').value,
            symptoms: document.getElementById('patientSymptoms').value,
            locationConsent: document.getElementById('locationConsent').checked
        };
    }
    
    switchTab(tabNumber) {
        // Update steps
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        for (let i = 1; i <= tabNumber; i++) {
            const step = document.getElementById(`step${i}`);
            if (i === tabNumber) {
                step.classList.add('active');
            } else {
                step.classList.add('completed');
            }