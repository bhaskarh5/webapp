#!/usr/bin/env python3
"""
Firebase Configuration Setup Helper
This script helps you easily configure Firebase credentials
"""

import json
import os
import sys

def setup_firebase():
    print("=" * 60)
    print("Firebase Configuration Setup")
    print("=" * 60)
    print("\nFollow these steps:")
    print("1. Go to https://console.firebase.google.com/")
    print("2. Click on your project")
    print("3. Click on Settings (gear icon) → Project Settings")
    print("4. Go to 'Service Accounts' tab")
    print("5. Click 'Generate New Private Key'")
    print("6. A JSON file will download")
    print("\n" + "=" * 60)
    
    print("\nPaste the JSON content from your Firebase config file below.")
    print("(Press Enter twice when done):\n")
    
    lines = []
    empty_lines = 0
    
    while empty_lines < 2:
        try:
            line = input()
            if line.strip() == "":
                empty_lines += 1
            else:
                empty_lines = 0
                lines.append(line)
        except EOFError:
            break
    
    if not lines:
        print("\n❌ No content provided. Exiting.")
        return False
    
    config_content = "\n".join(lines)
    
    try:
        config = json.loads(config_content)
        
        # Validate required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing = [f for f in required_fields if f not in config]
        
        if missing:
            print(f"\n❌ Invalid config. Missing fields: {', '.join(missing)}")
            return False
        
        # Save to file
        with open('firebase-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n✅ Firebase config saved successfully!")
        print(f"📦 Project ID: {config['project_id']}")
        print(f"📧 Service Account: {config['client_email']}")
        
        # Ask for bucket name
        print("\nNow enter your Firebase Storage bucket name:")
        print("(Format: 'your-project-name.appspot.com')")
        bucket = input("Bucket name: ").strip()
        
        if bucket:
            # Update app.py with the bucket name
            with open('app.py', 'r') as f:
                app_content = f.read()
            
            app_content = app_content.replace(
                "FIREBASE_BUCKET = 'your-project.appspot.com'",
                f"FIREBASE_BUCKET = '{bucket}'"
            )
            
            with open('app.py', 'w') as f:
                f.write(app_content)
            
            print(f"✅ Updated app.py with bucket: {bucket}")
        
        print("\n" + "=" * 60)
        print("✅ Firebase setup complete!")
        print("=" * 60)
        print("\nRestart the application for changes to take effect.")
        print("Run: python app.py")
        
        return True
        
    except json.JSONDecodeError:
        print("\n❌ Invalid JSON format. Please copy the entire JSON file content.")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    success = setup_firebase()
    sys.exit(0 if success else 1)
