import secrets
import hashlib
import string
from datetime import datetime, timedelta
from firebase_config import db
from typing import Optional, Dict, Any

class ActivationKeyManager:
    def __init__(self):
        self.collection_name = "activation_keys"
    
    def generate_activation_key(self, system_id: str, app_name: str = "wa-bomb") -> str:
        """
        Generate a unique activation key using only system_id and app_name
        Uses SHA-256 for wa-bomb, SHA-512 for mail-storm
        """
        # Create seed using only system_id and app_name with timestamp for uniqueness
        timestamp = datetime.now().isoformat()
        seed = f"{system_id}{app_name}{timestamp}{secrets.token_hex(8)}"
        
        # Choose hash algorithm based on app_name
        if app_name == "mail-storm":
            # Use SHA-512 for mail-storm
            hash_object = hashlib.sha512(seed.encode())
        else:
            # Use SHA-256 for wa-bomb (default)
            hash_object = hashlib.sha256(seed.encode())
            
        hex_hash = hash_object.hexdigest()
        
        # Convert to uppercase alphanumeric key (similar to your existing format)
        # Take first 16 characters and format with dashes
        raw_key = hex_hash[:16].upper()
        formatted_key = "-".join([raw_key[i:i+4] for i in range(0, len(raw_key), 4)])
        
        return formatted_key
    
    def store_activation_record(self, system_id: str, activation_key: str, 
                              app_name: str = "wa-bomb", customer_name: str = "", 
                              customer_mobile: str = "", customer_email: str = "",
                              validity_days: Optional[int] = None) -> bool:
        """
        Store activation record in Firebase Firestore
        """
        try:
            if not db:
                raise Exception("Firebase not initialized")
                
            # Calculate expiry date (None means never expires)
            expiry_date = None if validity_days is None else datetime.now() + timedelta(days=validity_days)
            
            # Create activation record
            activation_record = {
                "system_id": system_id,
                "activation_key": activation_key,
                "customer_name": customer_name,
                "customer_mobile": customer_mobile,
                "customer_email": customer_email,
                "created_at": datetime.now(),
                "expires_at": expiry_date,
                "is_active": True,
                "app_name": app_name,
                "validity_days": validity_days  # Store the original validity setting
            }
            
            # Store in Firestore using activation_key as document ID
            doc_ref = db.collection(self.collection_name).document(activation_key)
            doc_ref.set(activation_record)
            
            return True
            
        except Exception as e:
            print(f"Error storing activation record: {e}")
            return False
    
    def verify_activation(self, system_id: str, activation_key: str, app_name: str = "wa-bomb") -> Dict[str, Any]:
        """
        Verify if the system_id and activation_key pair exists and is valid
        """
        try:
            if not db:
                return {
                    "valid": False,
                    "message": "Database connection error",
                    "expired": False
                }
            
            # Get document by activation key
            doc_ref = db.collection(self.collection_name).document(activation_key)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {
                    "valid": False,
                    "message": "Invalid activation key",
                    "expired": False
                }
            
            data = doc.to_dict()
            
            # Check if system_id matches
            if data.get("system_id") != system_id:
                return {
                    "valid": False,
                    "message": "Activation key does not match this system",
                    "expired": False
                }
            
            # Check if app_name matches
            if data.get("app_name") != app_name:
                return {
                    "valid": False,
                    "message": f"Activation key is for {data.get('app_name', 'Unknown')} app, not {app_name}",
                    "expired": False
                }
            
            # Check if still active
            if not data.get("is_active", False):
                return {
                    "valid": False,
                    "message": "Activation key has been deactivated",
                    "expired": False
                }
            
            # Check expiry (skip check if expires_at is None - never expires)
            expires_at = data.get("expires_at")
            if expires_at is not None and expires_at < datetime.now():
                return {
                    "valid": False,
                    "message": "Activation key has expired",
                    "expired": True
                }
            
            return {
                "valid": True,
                "message": "Activation verified successfully",
                "expired": False,
                "customer_name": data.get("customer_name", ""),
                "customer_mobile": data.get("customer_mobile", ""),
                "customer_email": data.get("customer_email", ""),
                "expires_at": expires_at.isoformat() if expires_at else "Never expires",
                "validity_type": "lifetime" if expires_at is None else "limited"
            }
            
        except Exception as e:
            print(f"Error verifying activation: {e}")
            return {
                "valid": False,
                "message": f"Verification error: {str(e)}",
                "expired": False
            }
    
    def get_all_activations(self) -> list:
        """
        Get all activation records
        """
        try:
            if not db:
                return []
            
            docs = db.collection(self.collection_name).stream()
            activations = []
            
            for doc in docs:
                data = doc.to_dict()
                data['activation_key'] = doc.id
                activations.append(data)
            
            return activations
            
        except Exception as e:
            print(f"Error getting activations: {e}")
            return []
    
    def deactivate_key(self, activation_key: str) -> bool:
        """
        Deactivate an activation key
        """
        try:
            if not db:
                return False
            
            doc_ref = db.collection(self.collection_name).document(activation_key)
            doc_ref.update({"is_active": False})
            
            return True
            
        except Exception as e:
            print(f"Error deactivating key: {e}")
            return False
    
    def get_customer_statistics(self, customer_email: str) -> dict:
        """
        Get statistics for a customer by email
        """
        try:
            if not db:
                return {"error": "Database not initialized"}
            
            # Query all activations for this customer email
            docs = db.collection(self.collection_name).where("customer_email", "==", customer_email).stream()
            
            activations = []
            stats = {
                "total_keys": 0,
                "active_keys": 0,
                "expired_keys": 0,
                "deactivated_keys": 0,
                "apps": {},
                "customer_info": {}
            }
            
            for doc in docs:
                data = doc.to_dict()
                data['activation_key'] = doc.id
                activations.append(data)
                
                stats["total_keys"] += 1
                
                # Count by status
                if not data.get("is_active", False):
                    stats["deactivated_keys"] += 1
                else:
                    expires_at = data.get("expires_at")
                    if expires_at and expires_at < datetime.now():
                        stats["expired_keys"] += 1
                    else:
                        stats["active_keys"] += 1
                
                # Count by app
                app_name = data.get("app_name", "unknown")
                if app_name not in stats["apps"]:
                    stats["apps"][app_name] = {
                        "total": 0,
                        "active": 0,
                        "expired": 0,
                        "deactivated": 0
                    }
                
                stats["apps"][app_name]["total"] += 1
                if not data.get("is_active", False):
                    stats["apps"][app_name]["deactivated"] += 1
                elif expires_at and expires_at < datetime.now():
                    stats["apps"][app_name]["expired"] += 1
                else:
                    stats["apps"][app_name]["active"] += 1
                
                # Store customer info from the first record
                if not stats["customer_info"] and data.get("customer_name"):
                    stats["customer_info"] = {
                        "name": data.get("customer_name", ""),
                        "mobile": data.get("customer_mobile", ""),
                        "email": data.get("customer_email", "")
                    }
            
            stats["activations"] = activations
            return stats
            
        except Exception as e:
            print(f"Error getting customer statistics: {e}")
            return {"error": str(e)}