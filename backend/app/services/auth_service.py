from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from ..db.database import get_supabase_client

load_dotenv()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def verify_password(self, plain_password, hashed_password):
        """Verify password against hashed password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        """Get hash of password"""
        return pwd_context.hash(password)
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user with email and password"""
        response = self.supabase.table("users").select("*").eq("email", email).execute()
        
        if not response.data or len(response.data) == 0:
            return False
        
        user = response.data[0]
        if not self.verify_password(password, user["hashed_password"]):
            return False
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        response = self.supabase.table("users").select("*").eq("id", int(user_id)).execute()
        
        if not response.data or len(response.data) == 0:
            raise credentials_exception
        
        user = response.data[0]
        return user

auth_service = AuthService()