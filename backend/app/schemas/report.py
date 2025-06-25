from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class AppointmentStats(BaseModel):
    total: int
    completed: int
    scheduled: int
    cancelled: int

class ReportRequest(BaseModel):
    doctor_id: int
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    condition: Optional[str] = None

class DailyAppointmentCount(BaseModel):
    date: date
    count: int

class PatientCondition(BaseModel):
    condition: str
    count: int

class DoctorReport(BaseModel):
    doctor_id: int
    doctor_name: str
    report_date: datetime = datetime.now()
    appointment_stats: AppointmentStats
    daily_breakdown: Optional[List[DailyAppointmentCount]] = None
    common_conditions: Optional[List[PatientCondition]] = None
    summary: str