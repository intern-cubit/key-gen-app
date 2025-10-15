from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
from key_manager import ActivationKeyManager

app = FastAPI(title="Multi-App Activation Key Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize key manager
key_manager = ActivationKeyManager()

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
            raise HTTPException(status_code=500, detail="Failed to store activation record")
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating key: {str(e)}")

@app.post("/verify-key") 
async def verify_activation_key(request: VerifyKeyRequest):
    """
    Verify if system_id and activation_key pair is valid
    """
    try:
        result = key_manager.verify_activation(
            system_id=request.system_id,
            activation_key=request.activation_key,
            app_name=request.app_name
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying key: {str(e)}")

@app.get("/get-all-keys")
async def get_all_activation_keys():
    """
    Get all activation records (for admin use)
    """
    try:
        activations = key_manager.get_all_activations()
        return {
            "success": True,
            "activations": activations,
            "count": len(activations)
        }
        
    except Exception as e:
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
    return {"status": "healthy", "service": "Activation Key Manager"}

@app.post("/shutdown")
async def shutdown():
    """Shutdown endpoint for graceful termination"""
    import os
    import signal
    def shutdown_handler():
        os.kill(os.getpid(), signal.SIGTERM)
    
    # Schedule the shutdown to happen after the response is sent
    import asyncio
    asyncio.get_event_loop().call_later(0.5, shutdown_handler)
    return {"message": "Server shutting down..."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)