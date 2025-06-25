from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import date

class DoctorProfileCreate(BaseModel):
    specialization: str
    experience_years: int
    bio: Optional[str] = None

class PatientProfileCreate(BaseModel):
    date_of_birth: date
    blood_group: str
    medical_history: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: str
    doctor_profile: Optional[DoctorProfileCreate] = None
    patient_profile: Optional[PatientProfileCreate] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['doctor', 'patient']:
            raise ValueError('Role must be either "doctor" or "patient"')
        return v
    
    @validator('doctor_profile', 'patient_profile')
    def validate_profiles(cls, v, values):
        if 'role' in values:
            if values['role'] == 'doctor' and v is None and values.get('role') == 'doctor':
                raise ValueError('Doctor profile is required for doctor role')
            if values['role'] == 'patient' and v is None and values.get('role') == 'patient':
                raise ValueError('Patient profile is required for patient role')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

class ProfileData(BaseModel):
    id: int
    user_id: int
    # Other fields will be added dynamically

class UserWithProfile(UserResponse):
    profile: Optional[Dict[str, Any]] = None

class LoginResponse(Token):
    refresh_token: str
    user: UserWithProfile

class RefreshTokenRequest(BaseModel):
    refresh_token: str