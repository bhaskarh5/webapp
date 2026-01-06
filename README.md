# 🏥 MediAnalyze - Medical Report Analyzer

A full-stack web application that analyzes medical reports and provides instant insights on blood test results, identifying normal and abnormal values with possible causes.

## 🌐 Live Demo

**Frontend:** [https://test7-6b21a.web.app](https://test7-6b21a.web.app)

**Backend API:** [https://webapp-yqvj.onrender.com](https://webapp-yqvj.onrender.com)

## ✨ Features

- 📤 **Drag & Drop Upload** - Easy file upload for PDF, images (PNG, JPG)
- 🔍 **Intelligent Analysis** - Extracts and analyzes medical values from reports
- ⚡ **Instant Results** - Real-time processing with detailed breakdown
- 📊 **Value Classification** - Identifies normal, high, and low values
- 💡 **Cause Identification** - Suggests possible causes for abnormal readings
- 🔒 **Secure Storage** - Data stored in Firebase Realtime Database
- 📱 **Responsive Design** - Works on desktop and mobile devices

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript
- Firebase Hosting
- Modern gradient UI with animations

### Backend
- Python 3
- Flask (Web Framework)
- PyPDF2 (PDF text extraction)
- Pillow (Image processing)
- pytesseract (OCR)
- Firebase Admin SDK

### Database
- Firebase Realtime Database

### Deployment
- **Frontend:** Firebase Hosting
- **Backend:** Render (Free Tier)
- **Version Control:** GitHub

## 📋 How It Works

1. User uploads a medical report (PDF or image)
2. Frontend sends file to backend API via HTTPS
3. Backend extracts text using OCR/PDF parsing
4. AI analyzes medical values (blood pressure, glucose, cholesterol, etc.)
5. Results stored in Firebase Database
6. User sees analysis with normal/abnormal values and possible causes

## 🚀 Quick Start

### Using the Live App

1. Visit [https://test7-6b21a.web.app](https://test7-6b21a.web.app)
2. Upload a medical report (PDF, PNG, or JPG)
3. Click "Upload" and wait for analysis
4. View detailed results with recommendations

### Local Development

#### Prerequisites
- Python 3.11+
- Node.js (for Firebase CLI)
- Git

#### Setup

1. Clone the repository
```bash
git clone https://github.com/bhaskarh5/webapp.git
cd webapp
```

2. Install Python dependencies
```bash
pip install -r requirements.txt
```

3. Set up Firebase credentials
```bash
# Add your firebase-config.json with service account credentials
# Or set environment variable:
export FIREBASE_CONFIG_JSON='{"type":"service_account",...}'
export FIREBASE_DATABASE_URL='https://your-project.firebaseio.com'
```

4. Run the backend locally
```bash
python app.py
```

5. Deploy frontend to Firebase
```bash
firebase login
firebase init
firebase deploy
```

## 📁 Project Structure

```
webapp/
├── app.py                  # Flask backend API
├── index.html              # Main upload page
├── results.html            # Analysis results page
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
├── firebase.json          # Firebase hosting config
├── firebase-config.json   # Firebase credentials (gitignored)
├── public/                # Firebase hosting files
│   ├── index.html
│   ├── results.html
│   └── 404.html
└── README.md              # This file
```

## 🔒 Security

- Firebase credentials stored as environment variables on Render
- CORS enabled for secure cross-origin requests
- Uploaded files processed and deleted after analysis
- No permanent file storage on servers

## 🌟 Key Medical Values Analyzed

- Blood Pressure
- Glucose Levels
- Cholesterol
- Heart Rate
- Temperature
- Hemoglobin
- Complete Blood Count (CBC)
- And more...

## 🚧 Known Limitations

- **Render Free Tier:** Backend may spin down after inactivity (50s cold start)
- **OCR Accuracy:** Depends on image quality
- **Medical Disclaimer:** For informational purposes only, not medical advice

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**bhaskarh5**
- GitHub: [@bhaskarh5](https://github.com/bhaskarh5)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Note:** This application is for educational and informational purposes only. Always consult with qualified healthcare professionals for medical advice.
