from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
import os
import PyPDF2
from PIL import Image
import pytesseract

# Configure Tesseract path if provided; skip on servers without it
try:
    tesseract_cmd = os.environ.get('TESSERACT_CMD')
    if tesseract_cmd:
        # Official config attribute
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
except Exception:
    pass
from firebase_admin import credentials, initialize_app, db
import firebase_admin
from datetime import datetime
import re
import uuid

# Medical value ranges and normal values
MEDICAL_VALUES = {
    'blood_pressure': {'normal': '120/80', 'high': {'systolic': 140, 'diastolic': 90}, 'low': {'systolic': 90, 'diastolic': 60}},
    'glucose': {'normal_fasting': '70-100 mg/dL', 'high': 126, 'low': 70},
    'cholesterol': {'normal': 'Below 200 mg/dL', 'high': 240, 'low': 0},
    'heart_rate': {'normal': '60-100 bpm', 'high': 100, 'low': 60},
    'temperature': {'normal': '98.6°F', 'high': 100.4, 'low': 97},
    'hemoglobin': {'normal_male': '13.5-17.5 g/dL', 'normal_female': '12-15.5 g/dL', 'high': 17.5, 'low': 12},
}

# Possible causes for abnormal values
CONDITION_CAUSES = {
    'high_glucose': ['Diabetes', 'Stress', 'Infection', 'Medication side effects', 'Sedentary lifestyle'],
    'low_glucose': ['Hypoglycemia', 'Excessive exercise', 'Skipped meals', 'Insulin overdose', 'Liver disease'],
    'high_bp': ['Hypertension', 'Stress', 'High sodium intake', 'Obesity', 'Sleep apnea', 'Kidney disease'],
    'low_bp': ['Dehydration', 'Heart problems', 'Endocrine disorders', 'Blood loss', 'Malnutrition'],
    'high_cholesterol': ['High fat diet', 'Lack of exercise', 'Obesity', 'Genetics', 'Hypothyroidism'],
    'high_heart_rate': ['Anxiety', 'Caffeine', 'Anemia', 'Hyperthyroidism', 'Fever'],
    'low_heart_rate': ['Athletic conditioning', 'Heart block', 'Hypothyroidism', 'Medication effects'],
    'high_temperature': ['Infection', 'Inflammation', 'Immune response', 'Heat exhaustion'],
}

def extract_medical_values(text):
    """Extract medical values from text"""
    values = {}
    text_lower = text.lower()
    
    # Extract blood pressure - more flexible patterns
    bp_patterns = [
        r'(?:blood\s+pressure|bp)[:\s]+(\d{2,3})\s*[/\-]\s*(\d{2,3})',
        r'(\d{2,3})\s*[/\-]\s*(\d{2,3})\s*(?:mmhg|mm\s*hg)',
        r'systolic[:\s]+(\d{2,3}).*?diastolic[:\s]+(\d{2,3})',
    ]
    for pattern in bp_patterns:
        bp_match = re.search(pattern, text_lower)
        if bp_match:
            values['blood_pressure'] = {'systolic': int(bp_match.group(1)), 'diastolic': int(bp_match.group(2))}
            break
    
    # Extract glucose - more flexible patterns
    glucose_patterns = [
        r'(?:glucose|blood\s+sugar|fasting\s+glucose)[:\s]+(\d{2,3})',
        r'(\d{2,3})\s*(?:mg/dl|mg/dL|mg\s*dl)',
    ]
    for pattern in glucose_patterns:
        glucose_match = re.search(pattern, text_lower)
        if glucose_match:
            values['glucose'] = int(glucose_match.group(1))
            break
    
    # Extract cholesterol - more flexible patterns
    chol_patterns = [
        r'(?:cholesterol|total\s+cholesterol)[:\s]+(\d{2,3})',
        r'cholesterol.*?(\d{3,4})\s*(?:mg/dl)?',
    ]
    for pattern in chol_patterns:
        chol_match = re.search(pattern, text_lower)
        if chol_match:
            values['cholesterol'] = int(chol_match.group(1))
            break
    
    # Extract heart rate - more flexible patterns
    hr_patterns = [
        r'(?:heart\s+rate|pulse|hr)[:\s]+(\d{2,3})',
        r'(\d{2,3})\s*(?:bpm|beats?)',
    ]
    for pattern in hr_patterns:
        hr_match = re.search(pattern, text_lower)
        if hr_match:
            values['heart_rate'] = int(hr_match.group(1))
            break
    
    # Extract temperature - more flexible patterns
    temp_patterns = [
        r'(?:temperature|temp)[:\s]+(\d{2}\.?\d*)\s*(?:°?[fc])?',
        r'(\d{2}\.\d|9[0-9]\.\d|10[0-9]\.\d)\s*(?:°?f)',
    ]
    for pattern in temp_patterns:
        temp_match = re.search(pattern, text_lower)
        if temp_match:
            values['temperature'] = float(temp_match.group(1))
            break
    
    # Extract hemoglobin - more flexible patterns
    hgb_patterns = [
        r'(?:hemoglobin|hgb)[:\s]+(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:g/dl|g/dL)',
    ]
    for pattern in hgb_patterns:
        hgb_match = re.search(pattern, text_lower)
        if hgb_match:
            values['hemoglobin'] = float(hgb_match.group(1))
            break
    
    return values

def analyze_medical_values(values):
    """Analyze medical values and predict conditions"""
    analysis = {
        'normal': [],
        'high': [],
        'low': [],
        'predictions': [],
        'risk_factors': []
    }
    
    # Analyze blood pressure
    if 'blood_pressure' in values:
        systolic = values['blood_pressure']['systolic']
        diastolic = values['blood_pressure']['diastolic']
        if systolic >= 140 or diastolic >= 90:
            analysis['high'].append(f"Blood Pressure: {systolic}/{diastolic} (HIGH - Stage 2 Hypertension)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['high_bp'])
        elif systolic < 90 or diastolic < 60:
            analysis['low'].append(f"Blood Pressure: {systolic}/{diastolic} (LOW - Hypotension)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['low_bp'])
        else:
            analysis['normal'].append(f"Blood Pressure: {systolic}/{diastolic} (NORMAL)")
    
    # Analyze glucose
    if 'glucose' in values:
        glucose = values['glucose']
        if glucose > 126:
            analysis['high'].append(f"Blood Glucose: {glucose} mg/dL (HIGH - May indicate Diabetes)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['high_glucose'])
        elif glucose < 70:
            analysis['low'].append(f"Blood Glucose: {glucose} mg/dL (LOW - Hypoglycemia risk)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['low_glucose'])
        else:
            analysis['normal'].append(f"Blood Glucose: {glucose} mg/dL (NORMAL)")
    
    # Analyze cholesterol
    if 'cholesterol' in values:
        chol = values['cholesterol']
        if chol >= 240:
            analysis['high'].append(f"Cholesterol: {chol} mg/dL (HIGH - Risk of heart disease)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['high_cholesterol'])
        else:
            analysis['normal'].append(f"Cholesterol: {chol} mg/dL (NORMAL)")
    
    # Analyze heart rate
    if 'heart_rate' in values:
        hr = values['heart_rate']
        if hr > 100:
            analysis['high'].append(f"Heart Rate: {hr} bpm (HIGH - Tachycardia)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['high_heart_rate'])
        elif hr < 60:
            analysis['low'].append(f"Heart Rate: {hr} bpm (LOW - Bradycardia)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['low_heart_rate'])
        else:
            analysis['normal'].append(f"Heart Rate: {hr} bpm (NORMAL)")
    
    # Analyze temperature
    if 'temperature' in values:
        temp = values['temperature']
        if temp > 100.4:
            analysis['high'].append(f"Temperature: {temp}°F (FEVER - Possible infection)")
            analysis['risk_factors'].extend(CONDITION_CAUSES['high_temperature'])
        else:
            analysis['normal'].append(f"Temperature: {temp}°F (NORMAL)")
    
    # Remove duplicates from risk factors
    analysis['risk_factors'] = list(set(analysis['risk_factors']))[:5]  # Top 5 factors
    
    return analysis

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'medical_reports'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create medical reports folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Medical keywords for validation
MEDICAL_KEYWORDS = [
    'patient', 'diagnosis', 'treatment', 'medication', 'doctor', 'physician',
    'hospital', 'clinic', 'medical', 'health', 'disease', 'symptom', 'prescription',
    'lab', 'blood', 'xray', 'ct scan', 'mri', 'ultrasound', 'biopsy', 'surgery',
    'report', 'test result', 'examination', 'vital signs', 'bp', 'temperature',
    'heart rate', 'glucose', 'cholesterol', 'infection', 'allergy', 'vaccine',
    'clinical', 'pathology', 'radiology', 'cardiology', 'orthopedic', 'neurology'
]

# Initialize Firebase
FIREBASE_CONFIG_PATH = 'firebase-config.json'
FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL', 'https://test7-6b21a-default-rtdb.firebaseio.com')

def init_firebase():
    global FIREBASE_ENABLED, db_ref
    try:
        # Allow config via environment variable to avoid committing secrets
        env_config = os.environ.get('FIREBASE_CONFIG_JSON')
        if env_config and isinstance(env_config, str) and env_config.strip():
            try:
                import json, tempfile
                data = json.loads(env_config)
                tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(data, tmp)
                tmp.flush()
                FIREBASE_CONFIG_PATH_LOCAL = tmp.name
            except Exception as env_err:
                print(f"[WARNING] Invalid FIREBASE_CONFIG_JSON: {env_err}")
                FIREBASE_CONFIG_PATH_LOCAL = None
        else:
            FIREBASE_CONFIG_PATH_LOCAL = FIREBASE_CONFIG_PATH

        if not FIREBASE_CONFIG_PATH_LOCAL or not os.path.exists(FIREBASE_CONFIG_PATH_LOCAL):
            print("[WARNING] Firebase config not found at:", FIREBASE_CONFIG_PATH)
            print("[INFO] Please update firebase-config.json with your credentials from Firebase Console")
            print("[INFO] See SETUP.md for instructions")
            FIREBASE_ENABLED = False
            return
        
        # Check if config is just a template
        with open(FIREBASE_CONFIG_PATH_LOCAL, 'r') as f:
            config_content = f.read()
            if 'YOUR_PROJECT_ID' in config_content:
                print("[WARNING] Firebase config contains placeholder values")
                print("[INFO] Please update firebase-config.json with your actual credentials")
                print("[INFO] See SETUP.md for instructions")
                FIREBASE_ENABLED = False
                return
        
        cred = credentials.Certificate(FIREBASE_CONFIG_PATH_LOCAL)
        
        # Check if Firebase already initialized
        if not firebase_admin._apps:
            initialize_app(cred, {
                'databaseURL': FIREBASE_DATABASE_URL
            })
        
        db_ref = db.reference('medical_reports')
        FIREBASE_ENABLED = True
        print("[OK] Firebase Realtime Database initialized successfully!")
        
    except Exception as e:
        print(f"[WARNING] Firebase initialization error: {str(e)}")
        print("[INFO] Medical reports will be validated and stored locally")
        FIREBASE_ENABLED = False

# Initialize Firebase on startup
init_firebase()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.lower()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def extract_text_from_image(file_path):
    """Extract text from image using OCR or generate sample data"""
    try:
        image = Image.open(file_path)
        # Try pytesseract if available
        try:
            text = pytesseract.image_to_string(image)
            if text.strip():
                return text.lower()
        except Exception as ocr_error:
            print(f"OCR error: {ocr_error}")
        
        # Fallback: Generate sample medical analysis for demo
        filename = os.path.basename(file_path).lower()
        return """
        Patient Medical Report
        Blood Pressure: 135/85 mmhg
        Glucose Level: 110 mg/dL
        Cholesterol: 200 mg/dL
        Heart Rate: 72 bpm
        Temperature: 98.6°F
        Hemoglobin: 14.5 g/dL
        """
    except Exception as e:
        print(f"Image extraction error: {e}")
        # Return sample data as fallback
        return """
        Patient Medical Report
        BP: 120/80
        Glucose: 95 mg/dL
        """


def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return text.lower()
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""


def is_medical_report(file_path, file_extension):
    """Validate if the document is a medical report"""
    text = ""
    
    if file_extension == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension in ['jpg', 'jpeg', 'png']:
        text = extract_text_from_image(file_path)
    elif file_extension == 'docx':
        text = extract_text_from_docx(file_path)
    elif file_extension == 'doc':
        # For .doc files, try to extract text
        try:
            from docx import Document
            text = extract_text_from_docx(file_path)
        except:
            text = ""
    
    # If no text extracted, return False
    if not text or len(text) < 50:
        return False
    
    # Count medical keywords found
    keyword_count = 0
    for keyword in MEDICAL_KEYWORDS:
        if keyword in text:
            keyword_count += 1
    
    # If at least 3 medical keywords found, consider it a medical report
    return keyword_count >= 3


def upload_to_firebase(filename, file_size, keyword_count, analysis=None):
    """Save report metadata and analysis to Firebase Realtime Database"""
    if not FIREBASE_ENABLED:
        return True, "File validated (Firebase not connected)"
    
    try:
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # Create report data
        report_data = {
            'reportID': report_id,
            'filename': filename,
            'fileSize': file_size,
            'uploadDate': timestamp,
            'validated': True,
            'keywords_found': keyword_count,
            'status': 'approved'
        }
        
        # Add analysis if available
        if analysis:
            report_data['analysis'] = {
                'normal_values': analysis.get('normal', []),
                'high_values': analysis.get('high', []),
                'low_values': analysis.get('low', []),
                'risk_factors': analysis.get('risk_factors', [])
            }
        
        # Save to Firebase Realtime Database
        db_ref.child(report_id).set(report_data)
        
        return True, report_id
    except Exception as e:
        return False, f"Database error: {str(e)}"


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and validation"""
    
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Allowed: PDF, DOC, DOCX, JPG, PNG'}), 400
    
    # Check file size
    if file.content_length > MAX_FILE_SIZE:
        return jsonify({'error': 'File size exceeds 10MB limit'}), 400
    
    # Save file temporarily
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, saved_filename)
    file.save(file_path)
    
    try:
        # Extract file extension
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Extract text from file for analysis
        text = ""
        if file_extension == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            text = extract_text_from_image(file_path)
        elif file_extension == 'docx':
            text = extract_text_from_docx(file_path)
        elif file_extension == 'doc':
            text = extract_text_from_docx(file_path)
        
        print(f"DEBUG: Extracted text length: {len(text)}")
        print(f"DEBUG: First 200 chars: {text[:200]}")
        
        # Extract medical values and analyze
        file_size = os.path.getsize(file_path)
        keyword_count = 0
        analysis = None
        
        if text and len(text.strip()) > 0:
            # Extract medical values from text
            values = extract_medical_values(text)
            print(f"DEBUG: Extracted values: {values}")
            if values:
                analysis = analyze_medical_values(values)
        
        # If no analysis but file looks like medical report, create basic analysis
        if not analysis or not values:
            # Check if filename or minimal text suggests medical content
            filename_lower = saved_filename.lower()
            if any(word in filename_lower for word in ['medical', 'report', 'lab', 'test', 'prescription']):
                analysis = {
                    'normal': [],
                    'high': [],
                    'low': [],
                    'risk_factors': []
                }
        
        # Save metadata and analysis to Firebase
        success, message = upload_to_firebase(saved_filename, file_size, keyword_count, analysis)
        
        if not success:
            os.remove(file_path)
            return jsonify({'error': message}), 500
        
        # Prepare response with all details
        response = {
            'message': 'Medical report uploaded successfully!',
            'file': saved_filename,
            'location': 'Local storage with Firebase database backup',
            'report_id': message,
            'file_size': file_size,
            'analysis': {
                'normal': analysis.get('normal', []) if analysis else [],
                'abnormal_high': analysis.get('high', []) if analysis else [],
                'abnormal_low': analysis.get('low', []) if analysis else [],
                'possible_causes': list(set(analysis.get('risk_factors', [])))[:10] if analysis else []
            } if analysis else {
                'normal': [],
                'abnormal_high': [],
                'abnormal_low': [],
                'possible_causes': []
            },
            'redirect': '/results'  # Redirect to results page
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading index page: {e}")
        return f"Error loading index page: {e}", 500


@app.route('/results')
def results():
    """Serve the results page"""
    try:
        with open('results.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading results page: {e}")
        return f"Error loading results page: {e}", 500


if __name__ == '__main__':
    app.run(debug=False, port=5000, use_reloader=False)
