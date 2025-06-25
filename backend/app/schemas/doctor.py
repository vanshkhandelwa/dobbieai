from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class DoctorBase(BaseModel):
    specialization: str

class DoctorCreate(DoctorBase):
    email: EmailStr
    password: str
    full_name: str
    calendar_id: Optional[str] = None

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    is_active: Optional[bool] = None
    calendar_id: Optional[str] = None

class DoctorInDB(DoctorBase):
    id: int
    user_id: int
    created_at: datetime
    calendar_id: Optional[str] = None
    
    class Config:
        orm_mode = True

class DoctorWithUser(DoctorInDB):
    email: EmailStr
    full_name: str
    is_active: bool
    
    class Config:
        orm_mode = True