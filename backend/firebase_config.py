import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global variables
db = None
firebase_error = None
firebase_initialized = False

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account key"""
    global db, firebase_error, firebase_initialized
    
    try:
        # Path to your Firebase service account key JSON file
        service_account_path = os.path.join(os.path.dirname(__file__), "firebase-service-account.json")
        
        if not os.path.exists(service_account_path):
            error_msg = f"❌ Firebase service account file not found at: {service_account_path}"
            logger.error(error_msg)
            firebase_error = error_msg
            firebase_initialized = False
            return None
            
        logger.info(f"Loading Firebase credentials from: {service_account_path}")
        
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        
        # Don't test connection here to avoid blocking startup
        # Connection will be tested on first actual use
        logger.info("✅ Firebase credentials loaded successfully")
        logger.info("⚠️  Connection will be verified on first database operation")
        
        firebase_initialized = True
        firebase_error = None
        return db
        
    except FileNotFoundError as e:
        error_msg = f"❌ Firebase service account file not found: {str(e)}"
        logger.error(error_msg)
        firebase_error = error_msg
        firebase_initialized = False
        return None
        
    except ValueError as e:
        error_msg = f"❌ Invalid Firebase service account file format: {str(e)}"
        logger.error(error_msg)
        firebase_error = error_msg
        firebase_initialized = False
        return None
        
    except Exception as e:
        error_msg = f"❌ Error initializing Firebase: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        firebase_error = error_msg
        firebase_initialized = False
        return None

def get_firebase_status():
    """Get current Firebase connection status"""
    return {
        "initialized": firebase_initialized,
        "connected": db is not None,
        "error": firebase_error
    }

# Initialize Firestore client
db = initialize_firebase()