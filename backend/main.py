from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Local imports
from app.api.routes import appointments, reports, auth, doctors, patients
from app.db.database import Base, engine
from app.core.security import get_current_user, get_current_active_user, get_current_doctor, get_current_patient
from app.core.config import settings
from app.services.appointment_service import appointment_service
from app.services.llm_service import llm_service  # This should use Gemini

# Initialize FastAPI app
app = FastAPI(
    title="Doctor Appointment Assistant API",
    description="API for doctor appointment scheduling and management",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend URL
        "http://localhost:8000",  # Backend URL for development
        # Add production URLs as needed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Include all routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(doctors.router, prefix="/api/doctors", tags=["Doctors"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        supabase = get_supabase_client()
        response = supabase.table("users").select("count").limit(1).execute()
        db_status = "online" if response is not None else "offline"
        
        # Test Gemini API connection
        model = genai.GenerativeModel('gemini-1.5-flash')
        gemini_response = model.generate_content("Hello")
        gemini_status = "online" if gemini_response else "offline"
    except Exception as e:
        db_status = f"error: {str(e)}"
        gemini_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": db_status,
        "gemini_api": gemini_status,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# User endpoint - protected route example
@app.get("/api/users/me", response_model=Dict[str, Any])
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get current logged-in user information"""
    return current_user

# Doctor dashboard data endpoint
@app.get("/api/dashboard/doctor")
async def doctor_dashboard(current_doctor: Dict[str, Any] = Depends(get_current_doctor)):
    """Get doctor dashboard data"""
    today = datetime.now().date()
    doctor_id = current_doctor["doctor_profile"]["id"]
    
    # Get today's appointments
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    todays_appointments = appointment_service.get_doctor_appointments(doctor_id, today_start, today_end)
    
    # Get upcoming appointments (next 7 days)
    tomorrow = today + timedelta(days=1)
    week_end = today + timedelta(days=7)
    tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
    week_end_time = datetime.combine(week_end, datetime.max.time())
    upcoming_appointments = appointment_service.get_doctor_appointments(doctor_id, tomorrow_start, week_end_time)
    
    # Get appointment statistics
    supabase = get_supabase_client()
    
    # This month's appointments count
    first_day = today.replace(day=1)
    first_day_dt = datetime.combine(first_day, datetime.min.time())
    last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_day_dt = datetime.combine(last_day, datetime.max.time())
    
    monthly_response = supabase.table("appointments")\
        .select("count")\
        .eq("doctor_id", doctor_id)\
        .gte("date_time", first_day_dt.isoformat())\
        .lte("date_time", last_day_dt.isoformat())\
        .execute()
    
    monthly_count = monthly_response.count if hasattr(monthly_response, 'count') else 0
    
    # Status distribution
    status_response = supabase.table("appointments")\
        .select("status, count")\
        .eq("doctor_id", doctor_id)\
        .gte("date_time", first_day_dt.isoformat())\
        .execute()
    
    status_distribution = {}
    if status_response.data:
        for item in status_response.data:
            status_distribution[item.get('status', 'unknown')] = item.get('count', 0)
    
    # Result
    return {
        "today_appointments": todays_appointments,
        "upcoming_appointments": upcoming_appointments,
        "monthly_appointment_count": monthly_count,
        "status_distribution": status_distribution,
        "doctor_name": current_doctor["full_name"],
        "specialization": current_doctor["doctor_profile"]["specialization"],
        "timestamp": datetime.utcnow().isoformat()
    }

# Patient dashboard data endpoint
@app.get("/api/dashboard/patient")
async def patient_dashboard(current_patient: Dict[str, Any] = Depends(get_current_patient)):
    """Get patient dashboard data"""
    patient_id = current_patient["patient_profile"]["id"]
    
    # Get upcoming appointments
    today = datetime.now()
    upcoming_appointments = appointment_service.get_patient_appointments(patient_id, today)
    
    # Get past appointments
    past_appointments = appointment_service.get_patient_appointments(patient_id, None, today)
    
    # Get medical records
    supabase = get_supabase_client()
    records_response = supabase.table("medical_records")\
        .select("*")\
        .eq("patient_id", patient_id)\
        .order("date", desc=True)\
        .execute()
    
    medical_records = records_response.data if records_response.data else []
    
    # Get available doctors for new appointments
    doctors_response = supabase.table("doctors")\
        .select("*, users(id, full_name, email)")\
        .limit(10)\
        .execute()
    
    available_doctors = doctors_response.data if doctors_response.data else []
    
    return {
        "upcoming_appointments": upcoming_appointments,
        "past_appointments": past_appointments,
        "medical_records": medical_records,
        "available_doctors": available_doctors,
        "patient_name": current_patient["full_name"],
        "timestamp": datetime.utcnow().isoformat()
    }

# AI assistant endpoint for appointment suggestions using Gemini
@app.post("/api/assistant/appointment-suggestion")
async def get_appointment_suggestion(
    symptoms: str,
    medical_history: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get AI-powered appointment suggestion based on symptoms using Google's Gemini"""
    try:
        # Use the LLM service that's configured with Gemini
        recommendation = llm_service.analyze_medical_data({
            "symptoms": symptoms,
            "medical_history": medical_history or "Not provided",
            "patient_info": f"Patient: {current_user['full_name']}"
        })
        
        # Find matching doctors in the database
        supabase = get_supabase_client()
        
        # Extract likely specialization from recommendation
        specializations = ["Cardiologist", "Dermatologist", "Neurologist", "Gastroenterologist", 
                          "Orthopedic", "General Physician", "Psychiatrist", "Pediatrician"]
        
        matching_doctors = []
        for specialization in specializations:
            if specialization.lower() in recommendation.lower():
                # Found a potential match, search for doctors
                response = supabase.table("doctors")\
                    .select("*, users(full_name, email)")\
                    .ilike("specialization", f"%{specialization}%")\
                    .limit(3)\
                    .execute()
                
                if response.data and len(response.data) > 0:
                    matching_doctors.extend(response.data)
        
        # Return recommendation and matching doctors
        return {
            "recommendation": recommendation,
            "matching_doctors": matching_doctors[:3],  # Limit to top 3 matches
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

# Documentation customization
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = app.openapi()
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    openapi_schema["info"]["contact"] = {
        "name": "Vansh Khandelwal",
        "email": "vanshkhandelwal@example.com",
        "url": "https://github.com/vanshkhandelwal"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)