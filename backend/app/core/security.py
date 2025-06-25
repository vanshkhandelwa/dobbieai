from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from ..db.database import get_supabase_client

# Load environment variables
load_dotenv()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token with longer expiry"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 1 week
    to_encode.update({"exp": expire, "token_type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("token_type", "access")
        
        if token_type != "access":
            raise credentials_exception
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from Supabase
    supabase = get_supabase_client()
    response = supabase.table("users").select("*").eq("id", int(user_id)).execute()
    
    if not response.data or len(response.data) == 0:
        raise credentials_exception
    
    return response.data[0]

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Check if the current user is active"""
    if not current_user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_doctor(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get current doctor user"""
    if current_user["role"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Doctor role required."
        )
    
    # Get doctor details from Supabase
    supabase = get_supabase_client()
    response = supabase.table("doctors").select("*").eq("user_id", current_user["id"]).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    doctor_data = response.data[0]
    return {**current_user, "doctor_profile": doctor_data}

async def get_current_patient(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get current patient user"""
    if current_user["role"] != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Patient role required."
        )
    
    # Get patient details from Supabase
    supabase = get_supabase_client()
    response = supabase.table("patients").select("*").eq("user_id", current_user["id"]).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    patient_data = response.data[0]
    return {**current_user, "patient_profile": patient_data}