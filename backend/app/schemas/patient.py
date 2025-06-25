from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class PatientBase(BaseModel):
    date_of_birth: Optional[datetime] = None
    medical_history: Optional[str] = None

class PatientCreate(PatientBase):
    email: EmailStr
    password: str
    full_name: str

class PatientUpdate(BaseModel):
    date_of_birth: Optional[datetime] = None
    medical_history: Optional[str] = None
    is_active: Optional[bool] = None

class PatientInDB(PatientBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class PatientWithUser(BaseModel):
    id: int
    user_id: int
    date_of_birth: Optional[datetime] = None
    medical_history: Optional[str] = None
    created_at: datetime
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True