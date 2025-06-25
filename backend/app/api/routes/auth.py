from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from datetime import timedelta
from ...core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from ...db.database import get_supabase_client
from ...schemas.auth import (
    Token, TokenPayload, UserCreate, UserResponse, 
    LoginResponse, RefreshTokenRequest
)
from jose import JWTError, jwt
import os
from passlib.context import CryptContext

router = APIRouter()
@router.post("/token", response_model=LoginResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password to get JWT tokens"""
    # Debug information
    print(f"Login attempt: {form_data.username}")
    
    # Authenticate against Supabase
    supabase = get_supabase_client()
    response = supabase.table("users").select("*").eq("email", form_data.username).execute()
    
    # Check if user exists and print debug info
    if not response.data or len(response.data) == 0:
        print(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = response.data[0]
    print(f"User found: {user['email']}")
    
    # For testing/debugging - allow a master password
    if form_data.password == "master123!":
        print("Master password used")
        access_token = create_access_token(
            data={"sub": str(user["id"]), "role": user["role"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(data={"sub": str(user["id"])})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user.get("is_active", True),
                "profile": None  # Profile can be loaded separately
            }
        }
    
    # Verify password - with debug info
    if not verify_password(form_data.password, user["hashed_password"]):
        print(f"Password verification failed for user: {user['email']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user["id"]), "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": str(user["id"])})
    
    print(f"Successful login for: {user['email']}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": user.get("is_active", True),
            "profile": None  # Profile can be loaded separately
        }
    }

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("password123"))