from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..db.database import get_supabase_client

class AppointmentService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def get_available_slots(self, doctor_id: int, date: datetime.date) -> List[Dict]:
        """Get available appointment slots for a doctor on a specific date"""
        # Get doctor's schedule for the day
        day_of_week = date.weekday()
        schedule_response = self.supabase.table("schedules") \
            .select("*") \
            .eq("doctor_id", doctor_id) \
            .eq("day_of_week", day_of_week) \
            .execute()
        
        if not schedule_response.data:
            return []  # No schedule for this day
        
        schedule = schedule_response.data[0]
        start_time = datetime.strptime(schedule['start_time'], "%H:%M").time()
        end_time = datetime.strptime(schedule['end_time'], "%H:%M").time()
        
        # Get existing appointments for the day
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        appointments_response = self.supabase.table("appointments") \
            .select("date_time, duration_minutes") \
            .eq("doctor_id", doctor_id) \
            .gte("date_time", start_datetime.isoformat()) \
            .lt("date_time", end_datetime.isoformat()) \
            .execute()
        
        # Create a list of busy time slots
        busy_slots = []
        for appointment in appointments_response.data:
            appt_time = datetime.fromisoformat(appointment['date_time'])
            duration = appointment['duration_minutes']
            busy_slots.append({
                'start': appt_time,
                'end': appt_time + timedelta(minutes=duration)
            })
        
        # Generate available time slots
        available_slots = []
        slot_duration = 30  # 30-minute slots
        current_slot = start_datetime
        
        while current_slot < end_datetime:
            slot_end = current_slot + timedelta(minutes=slot_duration)
            
            # Check if slot overlaps with any busy slot
            is_available = True
            for busy in busy_slots:
                if (current_slot < busy['end'] and slot_end > busy['start']):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append({
                    'start_time': current_slot.strftime("%H:%M"),
                    'end_time': slot_end.strftime("%H:%M"),
                    'date': date.isoformat()
                })
            
            current_slot = slot_end
        
        return available_slots
    
    def create_appointment(self, appointment_data: Dict) -> Dict:
        """Create a new appointment"""
        response = self.supabase.table("appointments").insert(appointment_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def get_appointment(self, appointment_id: int) -> Dict:
        """Get appointment by ID"""
        response = self.supabase.table("appointments") \
            .select("*, doctors(*, users(full_name, email)), patients(*, users(full_name, email))") \
            .eq("id", appointment_id) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def update_appointment(self, appointment_id: int, update_data: Dict) -> Dict:
        """Update an appointment"""
        response = self.supabase.table("appointments") \
            .update(update_data) \
            .eq("id", appointment_id) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def cancel_appointment(self, appointment_id: int) -> Dict:
        """Cancel an appointment"""
        return self.update_appointment(appointment_id, {"status": "cancelled"})
    
    def get_doctor_appointments(self, doctor_id: int, from_date: Optional[datetime] = None, 
                                to_date: Optional[datetime] = None) -> List[Dict]:
        """Get doctor appointments with optional date range"""
        query = self.supabase.table("appointments") \
            .select("*, patients(id, user_id, patients.users(full_name, email))") \
            .eq("doctor_id", doctor_id)
        
        if from_date:
            query = query.gte("date_time", from_date.isoformat())
        if to_date:
            query = query.lte("date_time", to_date.isoformat())
        
        response = query.order("date_time").execute()
        return response.data
    
    def get_patient_appointments(self, patient_id: int, from_date: Optional[datetime] = None, 
                                to_date: Optional[datetime] = None) -> List[Dict]:
        """Get patient appointments with optional date range"""
        query = self.supabase.table("appointments") \
            .select("*, doctors(id, specialization, user_id, doctors.users(full_name))") \
            .eq("patient_id", patient_id)
        
        if from_date:
            query = query.gte("date_time", from_date.isoformat())
        if to_date:
            query = query.lte("date_time", to_date.isoformat())
        
        response = query.order("date_time").execute()
        return response.data

appointment_service = AppointmentService()