from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.db.models import AppointmentStatus

class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_time: datetime
    end_time: datetime
    reason: Optional[str] = None
    symptoms: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    patient_id: int

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    diagnosis: Optional[str] = None
    calendar_event_id: Optional[str] = None

class AppointmentInDB(AppointmentBase):
    id: int
    patient_id: int
    status: AppointmentStatus
    diagnosis: Optional[str] = None
    created_at: datetime
    calendar_event_id: Optional[str] = None
    
    class Config:
        orm_mode = True

class AppointmentWithDetails(AppointmentInDB):
    doctor_name: str
    patient_name: str
    
    class Config:
        orm_mode = True

class AvailabilitySlot(BaseModel):
    start_time: datetime
    end_time: datetime

class DoctorAvailability(BaseModel):
    doctor_id: int
    doctor_name: str
    available_slots: List[AvailabilitySlot]