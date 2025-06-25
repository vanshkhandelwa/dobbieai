from ..db.database import get_supabase_client

class SupabaseService:
    """Service to handle Supabase operations and provide compatibility with existing code"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    # User operations
    def get_user_by_email(self, email: str):
        response = self.client.table("users").select("*").eq("email", email).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def get_user(self, user_id: int):
        response = self.client.table("users").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def create_user(self, user_data: dict):
        response = self.client.table("users").insert(user_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    # Doctor operations
    def get_doctor_by_user_id(self, user_id: int):
        response = self.client.table("doctors").select("*").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def get_all_doctors(self):
        response = self.client.table("doctors").select("*, users(id, full_name, email)").execute()
        return response.data
    
    def get_doctor_availability(self, doctor_id: int, date=None):
        query = self.client.table("schedules").select("*").eq("doctor_id", doctor_id)
        if date:
            query = query.eq("day_of_week", date.weekday())
        response = query.execute()
        return response.data
    
    # Patient operations
    def get_patient_by_user_id(self, user_id: int):
        response = self.client.table("patients").select("*").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    # Appointment operations
    def create_appointment(self, appointment_data: dict):
        response = self.client.table("appointments").insert(appointment_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def get_doctor_appointments(self, doctor_id: int, from_date=None, to_date=None):
        query = self.client.table("appointments").select("*, patients(id, user_id, patients.users(full_name, email))").eq("doctor_id", doctor_id)
        if from_date:
            query = query.gte("date_time", from_date.isoformat())
        if to_date:
            query = query.lte("date_time", to_date.isoformat())
        response = query.execute()
        return response.data
    
    def get_patient_appointments(self, patient_id: int, from_date=None, to_date=None):
        query = self.client.table("appointments").select("*, doctors(id, user_id, doctors.users(full_name))").eq("patient_id", patient_id)
        if from_date:
            query = query.gte("date_time", from_date.isoformat())
        if to_date:
            query = query.lte("date_time", to_date.isoformat())
        response = query.execute()
        return response.data
    
    def update_appointment_status(self, appointment_id: int, status: str):
        response = self.client.table("appointments").update({"status": status}).eq("id", appointment_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    # Medical records
    def create_medical_record(self, record_data: dict):
        response = self.client.table("medical_records").insert(record_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    def get_patient_medical_records(self, patient_id: int):
        response = self.client.table("medical_records").select("*").eq("patient_id", patient_id).execute()
        return response.data
    
    # Reports
    def generate_appointment_report(self, doctor_id=None, from_date=None, to_date=None):
        query = self.client.table("appointments").select("*, doctors(specialization), patients(patients.users(full_name))")
        if doctor_id:
            query = query.eq("doctor_id", doctor_id)
        if from_date:
            query = query.gte("date_time", from_date.isoformat())
        if to_date:
            query = query.lte("date_time", to_date.isoformat())
        response = query.execute()
        return response.data