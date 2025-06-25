from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.db.database import get_db
from app.db import models
from app.schemas import appointment as appointment_schemas
from app.services.appointment_service import AppointmentService
from app.services.calendar_service import CalendarService
from app.services.email_service import EmailService

router = APIRouter(prefix="/appointments", tags=["appointments"])

appointment_service = AppointmentService()
calendar_service = CalendarService()
email_service = EmailService()

@router.get("/", response_model=List[appointment_schemas.AppointmentWithDetails])
async def get_appointments(
    doctor_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None),
    status: Optional[models.AppointmentStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get appointments with optional filters."""
    query = db.query(models.Appointment)
    
    if doctor_id:
        query = query.filter(models.Appointment.doctor_id == doctor_id)
    
    if patient_id:
        query = query.filter(models.Appointment.patient_id == patient_id)
    
    if status:
        query = query.filter(models.Appointment.status == status)
    
    if from_date:
        start_datetime = datetime.combine(from_date, datetime.min.time())
        query = query.filter(models.Appointment.appointment_time >= start_datetime)
    
    if to_date:
        end_datetime = datetime.combine(to_date, datetime.max.time())
        query = query.filter(models.Appointment.appointment_time <= end_datetime)
    
    # Get appointments and join with doctor and patient details
    appointments = query.all()
    
    # Enhance with doctor and patient names
    result = []
    for appointment in appointments:
        doctor_name = db.query(models.User).join(models.Doctor).filter(
            models.Doctor.id == appointment.doctor_id
        ).first().full_name
        
        patient_name = db.query(models.User).join(models.Patient).filter(
            models.Patient.id == appointment.patient_id
        ).first().full_name
        
        # Create enhanced appointment object
        appointment_dict = {
            "id": appointment.id,
            "doctor_id": appointment.doctor_id,
            "patient_id": appointment.patient_id,
            "appointment_time": appointment.appointment_time,
            "end_time": appointment.end_time,
            "status": appointment.status,
            "reason": appointment.reason,
            "symptoms": appointment.symptoms,
            "diagnosis": appointment.diagnosis,
            "created_at": appointment.created_at,
            "calendar_event_id": appointment.calendar_event_id,
            "doctor_name": doctor_name,
            "patient_name": patient_name
        }
        
        result.append(appointment_schemas.AppointmentWithDetails(**appointment_dict))
    
    return result

@router.get("/{appointment_id}", response_model=appointment_schemas.AppointmentWithDetails)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Get appointment by ID."""
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Get doctor and patient names
    doctor_name = db.query(models.User).join(models.Doctor).filter(
        models.Doctor.id == appointment.doctor_id
    ).first().full_name
    
    patient_name = db.query(models.User).join(models.Patient).filter(
        models.Patient.id == appointment.patient_id
    ).first().full_name
    
    # Create enhanced appointment object
    appointment_dict = {
        "id": appointment.id,
        "doctor_id": appointment.doctor_id,
        "patient_id": appointment.patient_id,
        "appointment_time": appointment.appointment_time,
        "end_time": appointment.end_time,
        "status": appointment.status,
        "reason": appointment.reason,
        "symptoms": appointment.symptoms,
        "diagnosis": appointment.diagnosis,
        "created_at": appointment.created_at,
        "calendar_event_id": appointment.calendar_event_id,
        "doctor_name": doctor_name,
        "patient_name": patient_name
    }
    
    return appointment_schemas.AppointmentWithDetails(**appointment_dict)

@router.post("/", response_model=appointment_schemas.AppointmentInDB, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: appointment_schemas.AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new appointment."""
    try:
        # Create appointment in database
        appointment = appointment_service.create_appointment(db, appointment_data)
        
        # Add to Google Calendar
        calendar_event_id = calendar_service.create_calendar_event(
            db,
            appointment.id,
            appointment_data.doctor_id,
            appointment_data.patient_id,
            appointment_data.appointment_time,
            appointment_data.end_time,
            appointment_data.reason
        )
        
        # Update appointment with calendar event ID
        if calendar_event_id:
            appointment_service.update_appointment_calendar_id(
                db, appointment.id, calendar_event_id
            )
        
        # Send email confirmation
        email_service.send_appointment_confirmation(
            db, appointment.id, appointment_data.doctor_id, appointment_data.patient_id
        )
        
        return appointment
    except HTTPException as e:
        # Re-raise HTTPExceptions
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment: {str(e)}"
        )

@router.put("/{appointment_id}", response_model=appointment_schemas.AppointmentInDB)
async def update_appointment(
    appointment_id: int,
    appointment_data: appointment_schemas.AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing appointment."""
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update fields
    for key, value in appointment_data.dict(exclude_unset=True).items():
        setattr(appointment, key, value)
    
    db.commit()
    db.refresh(appointment)
    
    return appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Cancel an appointment."""
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Mark as cancelled instead of deleting
    appointment.status = models.AppointmentStatus.CANCELLED
    db.commit()
    
    return

@router.get("/availability/{doctor_name}", response_model=List[appointment_schemas.DoctorAvailability])
async def check_doctor_availability(
    doctor_name: str,
    date: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Check doctor availability for a given date and time."""
    try:
        availability = appointment_service.check_doctor_availability(
            db, doctor_name, date, time_of_day
        )
        return availability
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking availability: {str(e)}"
        )