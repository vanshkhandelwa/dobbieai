import sys
from datetime import datetime, timedelta
import random
from passlib.context import CryptContext
from supabase import create_client

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Supabase connection details - replace the key with yours from Project Settings > API
SUPABASE_URL = "https://gjnkcyljdtwpqlrqfekm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdqbmtjeWxqZHR3cHFscnFmZWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MzE5MjYsImV4cCI6MjA2NjQwNzkyNn0.G_y1sK4jcTCxWL3V3R8ZB0yKfi1hfE88A8eOIjxff3g"  # Get this from your Supabase dashboard

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Connected to Supabase API!")
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    sys.exit(1)

# Create doctors
doctors_data = [
    {
        "email": "dr.ahuja@example.com",
        "full_name": "Dr. Vikram Ahuja",
        "specialization": "Cardiologist",
        "experience_years": 15,
        "bio": "Specialized in treating heart diseases with over 15 years of experience."
    },
    {
        "email": "dr.sharma@example.com",
        "full_name": "Dr. Priya Sharma",
        "specialization": "Dermatologist",
        "experience_years": 10,
        "bio": "Expert in skin disorders and cosmetic dermatology."
    },
    {
        "email": "dr.patel@example.com",
        "full_name": "Dr. Raj Patel",
        "specialization": "General Physician",
        "experience_years": 8,
        "bio": "Experienced in treating common illnesses and preventive healthcare."
    }
]

doctor_objects = []

for doctor_data in doctors_data:
    # Create user
    user_response = supabase.table("users").insert({
        "email": doctor_data["email"],
        "hashed_password": get_password_hash("password123"),
        "full_name": doctor_data["full_name"],
        "role": "doctor",
        "is_active": True
    }).execute()
    
    if len(user_response.data) > 0:
        user_id = user_response.data[0]['id']
        
        # Create doctor
        doctor_response = supabase.table("doctors").insert({
            "user_id": user_id,
            "specialization": doctor_data["specialization"],
            "experience_years": doctor_data["experience_years"],
            "bio": doctor_data["bio"]
        }).execute()
        
        if len(doctor_response.data) > 0:
            doctor_id = doctor_response.data[0]['id']
            doctor_objects.append({"id": doctor_id, "user_id": user_id})
            print(f"Created doctor: {doctor_data['full_name']}")

# Create patients
patients_data = [
    {
        "email": "patient1@example.com",
        "full_name": "Rahul Kumar",
        "date_of_birth": "1990-05-15",
        "blood_group": "O+",
        "medical_history": "No major issues"
    },
    {
        "email": "patient2@example.com",
        "full_name": "Anjali Desai",
        "date_of_birth": "1985-08-20",
        "blood_group": "AB+",
        "medical_history": "Asthma"
    },
    {
        "email": "vanshkhandelwal@example.com",
        "full_name": "Vansh Khandelwal",
        "date_of_birth": "1995-01-01",
        "blood_group": "B+",
        "medical_history": "No major issues"
    }
]

patient_objects = []

for patient_data in patients_data:
    # Create user
    user_response = supabase.table("users").insert({
        "email": patient_data["email"],
        "hashed_password": get_password_hash("password123"),
        "full_name": patient_data["full_name"],
        "role": "patient",
        "is_active": True
    }).execute()
    
    if len(user_response.data) > 0:
        user_id = user_response.data[0]['id']
        
        # Create patient
        patient_response = supabase.table("patients").insert({
            "user_id": user_id,
            "date_of_birth": patient_data["date_of_birth"],
            "blood_group": patient_data["blood_group"],
            "medical_history": patient_data["medical_history"]
        }).execute()
        
        if len(patient_response.data) > 0:
            patient_id = patient_response.data[0]['id']
            patient_objects.append({"id": patient_id, "user_id": user_id})
            print(f"Created patient: {patient_data['full_name']}")

# Create doctor schedules
for doctor in doctor_objects:
    # Create schedules for weekdays
    for day in range(0, 5):  # Monday to Friday
        schedule_response = supabase.table("schedules").insert({
            "doctor_id": doctor["id"],
            "day_of_week": day,
            "start_time": "09:00",
            "end_time": "17:00"
        }).execute()

# Create appointments
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

for i in range(5):
    appointment_date = today + timedelta(days=random.randint(1, 14))
    appointment_date = appointment_date.replace(hour=random.randint(9, 16), minute=0)
    
    doctor = random.choice(doctor_objects)
    patient = random.choice(patient_objects)
    
    # Create appointment
    appointment_response = supabase.table("appointments").insert({
        "doctor_id": doctor["id"],
        "patient_id": patient["id"],
        "date_time": appointment_date.isoformat(),
        "duration_minutes": 30,
        "reason": f"Consultation #{i+1}",
        "status": "scheduled",
        "created_at": datetime.now().isoformat()
    }).execute()

# Create specific appointment for you
your_patient = patient_objects[-1]  # The last patient we added (Vansh)
doctor = doctor_objects[0]  # Dr. Vikram Ahuja

# Tomorrow's appointment
tomorrow = today + timedelta(days=1)
tomorrow = tomorrow.replace(hour=10, minute=30)

supabase.table("appointments").insert({
    "doctor_id": doctor["id"],
    "patient_id": your_patient["id"],
    "date_time": tomorrow.isoformat(),
    "duration_minutes": 30,
    "reason": "Annual checkup",
    "status": "scheduled",
    "created_at": datetime.now().isoformat()
}).execute()

# Past appointment
last_week = today - timedelta(days=7)
last_week = last_week.replace(hour=14, minute=0)

supabase.table("appointments").insert({
    "doctor_id": doctor["id"],
    "patient_id": your_patient["id"],
    "date_time": last_week.isoformat(),
    "duration_minutes": 30,
    "reason": "Cold and fever",
    "status": "completed",
    "created_at": datetime.now().isoformat()
}).execute()

# Add medical record
supabase.table("medical_records").insert({
    "patient_id": your_patient["id"],
    "date": last_week.isoformat(),
    "diagnosis": "Common cold with mild fever",
    "prescription": "Paracetamol 500mg twice daily for 3 days; Rest and hydration recommended",
    "notes": "Follow up if symptoms persist beyond 5 days"
}).execute()

print("Database seeded successfully!")