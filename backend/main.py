from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
from key_manager import ActivationKeyManager
from firebase_config import get_firebase_status, db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-App Activation Key Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check Firebase status on startup
firebase_status = get_firebase_status()
if not firebase_status["initialized"]:
    logger.error("=" * 80)
    logger.error("❌ FIREBASE CONNECTION FAILED!")
    logger.error(f"Error: {firebase_status['error']}")
    logger.error("=" * 80)
    logger.warning("⚠️  Server will start but all database operations will fail!")
    logger.warning("⚠️  Please check your firebase-service-account.json file")
else:
    logger.info("=" * 80)
    logger.info("✅ FIREBASE CONNECTED SUCCESSFULLY!")
    logger.info("=" * 80)

# Initialize key manager
try:
    key_manager = ActivationKeyManager()
    logger.info("✅ Key manager initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize key manager: {str(e)}")
    key_manager = None

class GenerateKeyRequest(BaseModel):
    system_id: str
    app_name: str  # "wa-bomb" or "mail-storm"
    customer_name: Optional[str] = ""
    customer_mobile: Optional[str] = ""
    customer_email: Optional[str] = ""
    validity_days: Optional[int] = None  # None = never expires

class VerifyKeyRequest(BaseModel):
    system_id: str
    activation_key: str
    app_name: Optional[str] = "wa-bomb"  # Default for backward compatibility

@app.get("/")
async def root():
    return {
        "message": "Multi-App Activation Key Manager API",
        "version": "1.0.0",
        "supported_apps": ["wa-bomb", "mail-storm"],
        "endpoints": [
            "/generate-key",
            "/verify-key", 
            "/get-all-keys",
            "/deactivate-key",
            "/customer-stats/{email}"
        ]
    }

@app.post("/generate-key")
async def generate_activation_key(request: GenerateKeyRequest):
    """
    Generate a new activation key for a system ID
    """
    try:
        # Check Firebase connection first
        if not db:
            raise HTTPException(
                status_code=503, 
                detail="Firebase database is not connected. Please check server configuration and firebase-service-account.json file."
            )
        
        if not key_manager:
            raise HTTPException(
                status_code=503,
                detail="Key manager is not initialized. Server configuration error."
            )
        
        # Generate activation key using only system_id and app_name
        # SHA-256 for wa-bomb, SHA-512 for mail-storm
        activation_key = key_manager.generate_activation_key(
            system_id=request.system_id,
            app_name=request.app_name
        )
        
        # Store in database
        success = key_manager.store_activation_record(
            system_id=request.system_id,
            activation_key=activation_key,
            app_name=request.app_name,
            customer_name=request.customer_name,
            customer_mobile=request.customer_mobile,
            customer_email=request.customer_email,
            validity_days=request.validity_days
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store activation record in database")
        
        validity_message = "lifetime" if request.validity_days is None else f"{request.validity_days} days"
        
        return {
            "success": True,
            "activation_key": activation_key,
            "system_id": request.system_id,
            "app_name": request.app_name,
            "customer_name": request.customer_name,
            "customer_mobile": request.customer_mobile,
            "customer_email": request.customer_email,
            "validity_days": request.validity_days,
            "validity_type": "lifetime" if request.validity_days is None else "limited",
            "message": f"Activation key generated successfully for {request.app_name} with {validity_message} validity"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating key: {str(e)}")

@app.post("/verify-key") 
async def verify_activation_key(request: VerifyKeyRequest):
    """
    Verify if system_id and activation_key pair is valid
    """
    try:
        # Check Firebase connection first
        if not db:
            raise HTTPException(
                status_code=503, 
                detail="Firebase database is not connected. Cannot verify activation keys."
            )
        
        if not key_manager:
            raise HTTPException(
                status_code=503,
                detail="Key manager is not initialized. Server configuration error."
            )
        
        result = key_manager.verify_activation(
            system_id=request.system_id,
            activation_key=request.activation_key,
            app_name=request.app_name
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error verifying key: {str(e)}")

@app.get("/get-all-keys")
async def get_all_activation_keys():
    """
    Get all activation records (for admin use)
    """
    try:
        # Check Firebase connection first
        if not db:
            raise HTTPException(
                status_code=503, 
                detail="Firebase database is not connected. Cannot retrieve activation keys."
            )
        
        if not key_manager:
            raise HTTPException(
                status_code=503,
                detail="Key manager is not initialized. Server configuration error."
            )
        
        activations = key_manager.get_all_activations()
        return {
            "success": True,
            "activations": activations,
            "count": len(activations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting activations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting activations: {str(e)}")

@app.post("/deactivate-key")
async def deactivate_activation_key(activation_key: str = Form(...)):
    """
    Deactivate an activation key
    """
    try:
        success = key_manager.deactivate_key(activation_key)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to deactivate key")
        
        return {
            "success": True,
            "message": "Activation key deactivated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating key: {str(e)}")

@app.get("/customer-stats/{customer_email}")
async def get_customer_statistics(customer_email: str):
    """
    Get statistics for a customer by email - how many apps they have purchased
    """
    try:
        stats = key_manager.get_customer_statistics(customer_email)
        return {
            "success": True,
            "customer_email": customer_email,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Enhanced health check with Firebase status"""
    firebase_status = get_firebase_status()
    
    # Determine overall health
    is_healthy = firebase_status["initialized"] and firebase_status["connected"]
    
    response = {
        "status": "healthy" if is_healthy else "degraded",
        "service": "Activation Key Manager",
        "firebase": {
            "initialized": firebase_status["initialized"],
            "connected": firebase_status["connected"],
            "status": "✅ Connected" if is_healthy else "❌ Disconnected"
        }
    }
    
    # Add error details if Firebase is not working
    if not is_healthy:
        response["firebase"]["error"] = firebase_status["error"]
        response["warning"] = "Database operations will fail until Firebase is properly configured"
    
    return response

@app.get("/test-firebase")
async def test_firebase_connection():
    """Test Firebase connection by attempting to read from database"""
    try:
        if not db:
            return {
                "success": False,
                "message": "❌ Firebase is not initialized",
                "error": "Firebase database client is None"
            }
        
        # Try to perform a simple query
        logger.info("Testing Firebase connection...")
        test_collection = db.collection('activation_keys')
        query_result = test_collection.limit(1).stream()
        
        # Try to consume the iterator
        docs = list(query_result)
        
        return {
            "success": True,
            "message": "✅ Firebase connection is working!",
            "test_result": f"Successfully queried database (found {len(docs)} document(s) in test)"
        }
        
    except Exception as e:
        error_details = str(e)
        error_type = type(e).__name__
        
        # Check for specific Firebase errors
        if "invalid_grant" in error_details.lower() or "jwt signature" in error_details.lower():
            error_message = "❌ Firebase credentials are invalid or expired (Invalid JWT Signature)"
            solution = "Please update your firebase-service-account.json file with valid credentials from Firebase Console"
        elif "permission" in error_details.lower():
            error_message = "❌ Firebase credentials don't have sufficient permissions"
            solution = "Check your service account permissions in Firebase Console"
        elif "not found" in error_details.lower():
            error_message = "❌ Firebase project or collection not found"
            solution = "Verify your Firebase project ID and database settings"
        else:
            error_message = f"❌ Firebase connection error: {error_type}"
            solution = "Check your network connection and Firebase credentials"
        
        logger.error(f"Firebase test failed: {error_details}")
        
        return {
            "success": False,
            "message": error_message,
            "error": error_details,
            "error_type": error_type,
            "solution": solution
        }

@app.post("/shutdown")
async def shutdown():
    """Shutdown endpoint for graceful termination"""
    logger.info("Shutdown endpoint called. Initiating graceful shutdown...")
    
    # Send response before shutting down
    import asyncio
    
    async def shutdown_server():
        await asyncio.sleep(0.5)  # Give time for response to be sent
        logger.info("Shutting down server now...")
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)
    
    # Schedule the shutdown
    asyncio.create_task(shutdown_server())
    
    return {"message": "Server shutting down gracefully...", "status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)