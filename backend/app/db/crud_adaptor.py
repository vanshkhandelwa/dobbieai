from .session import get_supabase_session

# User operations
def get_user_by_email(email: str):
    db = get_supabase_session()
    response = db.table("users").select("*").eq("email", email).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def get_user(user_id: int):
    db = get_supabase_session()
    response = db.table("users").select("*").eq("id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def create_user(user_data: dict):
    db = get_supabase_session()
    response = db.table("users").insert(user_data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

# Doctor operations
def get_doctor_by_user_id(user_id: int):
    db = get_supabase_session()
    response = db.table("doctors").select("*").eq("user_id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def get_all_doctors():
    db = get_supabase_session()
    response = db.table("doctors").select("*, users(id, full_name, email)").execute()
    return response.data

# Patient operations
def get_patient_by_user_id(user_id: int):
    db = get_supabase_session()
    response = db.table("patients").select("*").eq("user_id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

# Appointment operations
def create_appointment(appointment_data: dict):
    db = get_supabase_session()
    response = db.table("appointments").insert(appointment_data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def get_doctor_appointments(doctor_id: int):
    db = get_supabase_session()
    response = db.table("appointments").select("*, patients(id, user_id, patients.users(full_name, email))").eq("doctor_id", doctor_id).execute()
    return response.data

def get_patient_appointments(patient_id: int):
    db = get_supabase_session()
    response = db.table("appointments").select("*, doctors(id, user_id, doctors.users(full_name))").eq("patient_id", patient_id).execute()
    return response.data

def update_appointment_status(appointment_id: int, status: str):
    db = get_supabase_session()
    response = db.table("appointments").update({"status": status}).eq("id", appointment_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None