# How to Add Firebase - Step by Step Guide

## Step 1: Go to Firebase Console
1. Open https://console.firebase.google.com/
2. Sign in with your Google account (create one if needed)

---

## Step 2: Create a New Project (if you don't have one)

### 2a. Click "Create a project"
```
┌─────────────────────────────────────┐
│  Welcome to Firebase              │
│  [+ Create a project]               │
└─────────────────────────────────────┘
```

### 2b. Enter Project Details
- **Project name**: `MedicalReportApp` (or any name)
- **Enable Google Analytics**: No (for testing)
- Click **Create project**

Wait 1-2 minutes for setup...

---

## Step 3: Set Up Cloud Storage

### 3a. Click "Storage" in Left Menu
```
Left Menu:
├── Build
│   ├── Realtime Database
│   ├── Firestore Database
│   ├── Storage ← CLICK HERE
│   └── Hosting
```

### 3b. Click "Get Started" or "Create bucket"
- Choose: **Start in production mode**
- Region: Select your location (e.g., `us-east1`)
- Click **Create**

**Your Bucket Name will be visible:**
```
gs://your-project-12345.appspot.com
```
**Save this!** You'll need it in Step 5.

---

## Step 4: Get Service Account Credentials

### 4a. Go to Project Settings
1. Click the **Settings ⚙️ icon** (top left)
2. Select **Project Settings**

### 4b. Go to "Service Accounts" Tab
```
Tabs: Project Settings | Service Accounts ← CLICK HERE
```

### 4c. Click "Generate New Private Key"
```
┌────────────────────────────────────────┐
│  Firebase Admin SDK                   │
│  [Generate New Private Key] ← CLICK   │
└────────────────────────────────────────┘
```

### 4d. A JSON File Downloads Automatically
- File name: something like `project-name-xxxxx.json`
- **Keep it safe!** This file has secret credentials

---

## Step 5: Add Credentials to Your App

### Option A: Using Automated Script (Easiest)

**Run this command:**
```bash
python setup_firebase.py
```

**Then:**
1. Open the downloaded JSON file
2. Copy ALL the content (Ctrl+A, Ctrl+C)
3. Paste it into the terminal when asked
4. Press Enter twice
5. Enter your bucket name (from Step 3b)

**Done!** ✅

---

### Option B: Manual Setup

**Step 5b-1: Copy JSON Content**
1. Open your downloaded JSON file with a text editor
2. Select all content (Ctrl+A)
3. Copy it (Ctrl+C)

**Step 5b-2: Update firebase-config.json**
1. In your project folder, open `firebase-config.json`
2. Delete all existing content
3. Paste the JSON (Ctrl+V)
4. Save (Ctrl+S)

**Example of what it should look like:**
```json
{
  "type": "service_account",
  "project_id": "medical-report-app-12345",
  "private_key_id": "abcdef1234567890",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xyz@medical-report-app-12345.iam.gserviceaccount.com",
  "client_id": "123456789",
  ...
}
```

**Step 5b-3: Update Bucket Name in app.py**
1. Open `app.py`
2. Find line 31:
   ```python
   FIREBASE_BUCKET = 'your-project.appspot.com'
   ```
3. Replace with your bucket name from Step 3b:
   ```python
   FIREBASE_BUCKET = 'medical-report-app-12345.appspot.com'
   ```
4. Save the file

---

## Step 6: Restart the App

Stop the Flask app (if running) and restart:

```bash
python app.py
```

You should see in the terminal:
```
✅ Firebase initialized successfully!
 * Running on http://127.0.0.1:5000
```

---

## Step 7: Test It!

1. Open http://localhost:5000 in your browser
2. Upload a medical report
3. You should see: **"Medical report validated and uploaded to cloud storage successfully!"**
4. Check Firebase Console → Storage to see your uploaded file

---

## Verification Checklist

✓ Created Firebase project
✓ Set up Cloud Storage bucket
✓ Downloaded service account JSON
✓ Added JSON to `firebase-config.json`
✓ Updated bucket name in `app.py`
✓ Restarted Flask app
✓ See "Firebase initialized successfully!" message

---

## What Happens After Setup?

When you upload a medical report:

```
1. File uploaded from browser
   ↓
2. Backend validates it's a medical document
   ↓
3. If valid: Upload to Firebase Cloud Storage
   ✅ File stored in: gs://bucket-name/medical_reports/YYYYMMDD_HHMMSS_filename
   ↓
4. User sees success message
```

---

## Common Issues & Fixes

**Issue: "Firebase config contains placeholder values"**
```
❌ Wrong: firebase-config.json still has "YOUR_PROJECT_ID"
✅ Fix: Replace with actual values from downloaded JSON
```

**Issue: "Bucket not found"**
```
❌ Wrong: FIREBASE_BUCKET = 'your-project.appspot.com'
✅ Fix: Use actual bucket from Firebase Storage:
         FIREBASE_BUCKET = 'medical-report-12345.appspot.com'
```

**Issue: JSON file not found**
```
❌ Wrong: Placed JSON file in wrong location
✅ Fix: Put firebase-config.json in project root folder:
         c:\Users\ramya\OneDrive\Desktop\bhaskar\
```

**Issue: "Permission denied" error**
```
❌ Wrong: Using wrong credentials
✅ Fix: Make sure you downloaded JSON from Service Accounts tab
         (not from any other place)
```

---

## Where to Find Your Values

| Value | Where to Find |
|-------|---------------|
| Bucket Name | Firebase Console → Storage (top of page) |
| Project ID | Settings ⚙️ → Project Settings (near top) |
| Service Account JSON | Settings ⚙️ → Service Accounts → Generate Key |

---

## Need Help?

- **Firebase docs**: https://firebase.google.com/docs
- **Cloud Storage guide**: https://firebase.google.com/docs/storage
- **Service Account setup**: https://firebase.google.com/docs/admin/setup

---

**That's it!** Your medical report app is now connected to Firebase! 🎉
