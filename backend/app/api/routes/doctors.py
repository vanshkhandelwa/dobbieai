from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import models
from app.schemas import doctor as doctor_schemas
from app.core.security import get_password_hash

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("/", response_model=List[doctor_schemas.DoctorWithUser])
async def get_doctors(db: Session = Depends(get_db)):
    """Get all doctors."""
    doctors = db.query(models.Doctor).join(models.User).filter(models.User.is_active == True).all()
    
    result = []
    for doctor in doctors:
        doctor_dict = {
            "id": doctor.id,
            "user_id": doctor.user_id,
            "specialization": doctor.specialization,
            "created_at": doctor.created_at,
            "calendar_id": doctor.calendar_id,
            "email": doctor.user.email,
            "full_name": doctor.user.full_name,
            "is_active": doctor.user.is_active
        }
        result.append(doctor_schemas.DoctorWithUser(**doctor_dict))
    
    return result

@router.get("/{doctor_id}", response_model=doctor_schemas.DoctorWithUser)
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get a doctor by ID."""
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor_dict = {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "specialization": doctor.specialization,
        "created_at": doctor.created_at,
        "calendar_id": doctor.calendar_id,
        "email": doctor.user.email,
        "full_name": doctor.user.full_name,
        "is_active": doctor.user.is_active
    }
    
    return doctor_schemas.DoctorWithUser(**doctor_dict)

@router.post("/", response_model=doctor_schemas.DoctorWithUser, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_data: doctor_schemas.DoctorCreate,
    db: Session = Depends(get_db)
):
    """Create a new doctor."""
    # Check if email already exists
    if db.query(models.User).filter(models.User.email == doctor_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = models.User(
        email=doctor_data.email,
        hashed_password=get_password_hash(doctor_data.password),
        full_name=doctor_data.full_name,
        role=models.UserRole.DOCTOR,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create doctor profile
    doctor = models.Doctor(
        user_id=user.id,
        specialization=doctor_data.specialization,
        calendar_id=doctor_data.calendar_id
    )
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    
    # Return combined doctor and user information
    doctor_dict = {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "specialization": doctor.specialization,
        "created_at": doctor.created_at,
        "calendar_id": doctor.calendar_id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    }
    
    return doctor_schemas.DoctorWithUser(**doctor_dict)

@router.put("/{doctor_id}", response_model=doctor_schemas.DoctorWithUser)
async def update_doctor(
    doctor_id: int,
    doctor_data: doctor_schemas.DoctorUpdate,
    db: Session = Depends(get_db)
):
    """Update a doctor."""
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Update doctor fields
    for key, value in doctor_data.dict(exclude_unset=True).items():
        if key == "is_active":
            # Update user.is_active
            doctor.user.is_active = value
        else:
            # Update doctor fields
            setattr(doctor, key, value)
    
    db.commit()
    db.refresh(doctor)
    
    # Return updated doctor
    doctor_dict = {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "specialization": doctor.specialization,
        "created_at": doctor.created_at,
        "calendar_id": doctor.calendar_id,
        "email": doctor.user.email,
        "full_name": doctor.user.full_name,
        "is_active": doctor.user.is_active
    }
    
    return doctor_schemas.DoctorWithUser(**doctor_dict)