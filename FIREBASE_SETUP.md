# Quick Firebase Setup Guide

## Option 1: Using Automated Setup Script (Recommended)

Run this command:
```bash
python setup_firebase.py
```

Then follow the prompts to paste your Firebase credentials.

---

## Option 2: Manual Setup

### Step 1: Get Firebase Credentials

1. **Create Firebase Project** (if you don't have one):
   - Go to https://console.firebase.google.com/
   - Click "Create a Project"
   - Enter a project name
   - Enable Google Analytics (optional)
   - Click "Create Project"

2. **Download Service Account JSON**:
   - Click the **Settings gear icon** (⚙️) at the top left
   - Click **Project Settings**
   - Go to **Service Accounts** tab
   - Click **Generate New Private Key**
   - A JSON file will download automatically

3. **Copy the JSON content**

### Step 2: Update firebase-config.json

1. Open `firebase-config.json` in this folder
2. Delete all content and paste your downloaded JSON
3. Save the file

### Step 3: Get Your Firebase Bucket Name

1. In Firebase Console, click **Storage** in the left menu
2. You'll see a bucket like: `your-project-12345.appspot.com`
3. Copy this bucket name

### Step 4: Update app.py

1. Open `app.py`
2. Find this line (around line 31):
   ```python
   FIREBASE_BUCKET = 'your-project.appspot.com'
   ```
3. Replace `your-project.appspot.com` with your actual bucket name
4. Save the file

### Step 5: Restart the App

```bash
python app.py
```

You should see:
```
✅ Firebase initialized successfully!
```

---

## Verification

After setup, try uploading a medical report:
- Valid medical report → ✅ Uploads to Firebase Cloud Storage
- Non-medical document → ❌ Shows error message

---

## Troubleshooting

**Error: "Firebase config contains placeholder values"**
- You didn't replace the values in firebase-config.json
- Copy and paste the actual credentials from your Firebase project

**Error: "Invalid JSON format"**
- Make sure you copied the entire JSON file
- Check there are no extra characters

**Error: "Bucket not found"**
- Make sure the bucket name in app.py matches your Firebase Storage bucket exactly
- The bucket should be in format: `project-name-12345.appspot.com`

**Still seeing placeholder warning?**
- Restart the Flask app: `python app.py`
- Wait for the message: `✅ Firebase initialized successfully!`

---

## File Locations

- `firebase-config.json` - Your Firebase credentials (keep this secret!)
- `app.py` - Backend code (update bucket name here)
- `setup_firebase.py` - Automated setup helper script

Never commit `firebase-config.json` to version control!
