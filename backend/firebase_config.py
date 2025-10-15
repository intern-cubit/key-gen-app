import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account key"""
    try:
        # Path to your Firebase service account key JSON file
        service_account_path = os.path.join(os.path.dirname(__file__), "firebase-service-account.json")
        
        if not os.path.exists(service_account_path):
            print("Firebase service account file not found. Please add firebase-service-account.json")
            return None
            
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

# Initialize Firestore client
db = initialize_firebase()