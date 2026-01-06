# Medical Report Upload System - Setup Guide

## Features
✓ Drag & drop file upload
✓ Medical report validation
✓ Cloud storage integration with Firebase
✓ Automatic error handling

## Prerequisites
1. Python 3.8+
2. Firebase Project (free tier available)
3. Tesseract OCR (for image text extraction)

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR
**On Windows:**
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Run the installer (default path: `C:\Program Files\Tesseract-OCR`)
- Add to app.py: `pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

**On macOS:**
```bash
brew install tesseract
```

**On Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 3. Setup Firebase

#### Step 3a: Create Firebase Project
1. Go to https://console.firebase.google.com/
2. Click "Create a project"
3. Follow the setup wizard
4. Enable "Google Cloud Storage"

#### Step 3b: Get Firebase Credentials
1. Go to Project Settings (gear icon)
2. Click "Service Accounts" tab
3. Click "Generate New Private Key"
4. Save the JSON file as `firebase-config.json` in the project folder

#### Step 3c: Update app.py
1. Replace `'your-project.appspot.com'` with your actual Firebase bucket name
   - Find it in Firebase Console > Storage > Bucket name
   - Example: `my-project-12345.appspot.com`

### 4. Run the Application

```bash
python app.py
```

The application will run at: `http://localhost:5000`

## Medical Report Validation

The system validates documents by:
1. Extracting text from uploaded files (PDF, DOC, DOCX, or images)
2. Searching for medical keywords (diagnosis, treatment, patient, etc.)
3. Requiring at least 3 medical keywords to be found
4. Rejecting files that don't meet the criteria

### Medical Keywords Detected:
- patient, diagnosis, treatment, medication, doctor, physician
- hospital, clinic, medical, health, disease, symptom, prescription
- lab, blood, xray, ct scan, mri, ultrasound, biopsy, surgery
- report, test result, examination, vital signs, bp, temperature
- And 20+ more medical terms

## Cloud Storage

Valid medical reports are automatically:
1. Validated for medical content
2. Uploaded to Firebase Cloud Storage
3. Organized by timestamp: `medical_reports/YYYYMMDD_HHMMSS_filename`

## File Limits
- Maximum size: 10 MB
- Allowed formats: PDF, DOC, DOCX, JPG, JPEG, PNG

## Troubleshooting

**Issue: "Module not found" errors**
- Solution: `pip install -r requirements.txt`

**Issue: Tesseract not found**
- Solution: Install Tesseract OCR and update the path in app.py

**Issue: Firebase not configured**
- Solution: 
  1. Download firebase-config.json from Firebase Console
  2. Place it in the project folder
  3. Restart the app

**Issue: File rejected as non-medical**
- Ensure your document contains medical keywords
- Check that text extraction is working (especially for images)
- For low-quality images, the OCR might fail to extract text

## File Structure
```
bhaskar/
├── index.html              # Frontend interface
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── firebase-config.json    # Firebase credentials (you need to add this)
└── temp_uploads/           # Temporary storage (auto-created)
```

## Security Notes
- Never commit firebase-config.json to version control
- Files are temporarily stored in `temp_uploads/` and deleted after upload
- Use HTTPS in production
- Implement user authentication for production use

## API Endpoint
```
POST /upload
Content-Type: multipart/form-data

Request:
- file: The medical report file

Response:
{
  "message": "Medical report validated and uploaded to cloud storage successfully!"
}

Error Response:
{
  "error": "Error message describing what went wrong"
}
```
