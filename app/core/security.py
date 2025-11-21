# app/core/security.py
from passlib.context import CryptContext
import bcrypt

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_pin(pin: str) -> str:
    """Hash a PIN using bcrypt"""
    try:
        # Ensure PIN is exactly 4 digits
        if len(pin) != 4 or not pin.isdigit():
            raise ValueError("PIN must be exactly 4 digits")
        
        pin_bytes = pin.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pin_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        raise ValueError(f"PIN hashing failed: {str(e)}")

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Verify a PIN against its hash"""
    try:
        # Ensure PIN is exactly 4 digits
        if len(plain_pin) != 4 or not plain_pin.isdigit():
            return False
        
        pin_bytes = plain_pin.encode('utf-8')
        hashed_bytes = hashed_pin.encode('utf-8')
        return bcrypt.checkpw(pin_bytes, hashed_bytes)
    except Exception:
        return False