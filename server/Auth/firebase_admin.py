import firebase_admin
from firebase_admin import credentials, auth
import os

# Initialize Firebase Admin SDK
# You'll need to download your service account key from Firebase Console
# Go to Project Settings > Service Accounts > Generate New Private Key

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            # You need to download your service account key from Firebase Console
            # and place it in your backend directory
            service_account_path = "vibescape-58630-firebase-adminsdk-fbsvc-967bb3a808.json"
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin SDK initialized successfully")
            else:
                print("⚠️  Firebase service account key not found!")
                print("Please download your service account key from Firebase Console:")
                print("1. Go to Firebase Console > Project Settings")
                print("2. Go to Service Accounts tab")
                print("3. Click 'Generate New Private Key'")
                print("4. Save the JSON file as 'vibescape-58630-firebase-adminsdk-fbsvc-967bb3a808.json' in your backend directory")
                return False
        return True
    except Exception as e:
        print(f"❌ Error initializing Firebase Admin SDK: {e}")
        return False

def verify_firebase_token(id_token):
    """Verify Firebase ID token and return user info"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            'success': True,
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name'),
            'picture': decoded_token.get('picture')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_user_by_uid(uid):
    """Get user info from Firebase Auth"""
    try:
        user = auth.get_user(uid)
        return {
            'success': True,
            'user': {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def create_user_in_firebase(email, password, display_name=None):
    """Create a new user in Firebase Auth"""
    try:
        user_properties = {
            'email': email,
            'password': password,
            'email_verified': False
        }
        
        if display_name:
            user_properties['display_name'] = display_name
            
        user = auth.create_user(**user_properties)
        return {
            'success': True,
            'uid': user.uid,
            'user': {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def delete_user_from_firebase(uid):
    """Delete a user from Firebase Auth"""
    try:
        auth.delete_user(uid)
        return {'success': True}
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        } 