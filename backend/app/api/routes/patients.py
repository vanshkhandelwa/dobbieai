from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import models
from app.schemas import patient as patient_schemas
from app.core.security import get_password_hash

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[patient_schemas.PatientWithUser])
async def get_patients(db: Session = Depends(get_db)):
    """Get all patients."""
    patients = db.query(models.Patient).join(models.User).filter(models.User.is_active == True).all()
    
    result = []
    for patient in patients:
        patient_dict = {
            "id": patient.id,
            "user_id": patient.user_id,
            "date_of_birth": patient.date_of_birth,
            "medical_history": patient.medical_history,
            "created_at": patient.created_at,
            "email": patient.user.email,
            "full_name": patient.user.full_name,
            "is_active": patient.user.is_active
        }
        result.append(patient_schemas.PatientWithUser(**patient_dict))
    
    return result

@router.get("/{patient_id}", response_model=patient_schemas.PatientWithUser)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get a patient by ID."""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "date_of_birth": patient.date_of_birth,
        "medical_history": patient.medical_history,
        "created_at": patient.created_at,
        "email": patient.user.email,
        "full_name": patient.user.full_name,
        "is_active": patient.user.is_active
    }
    
    return patient_schemas.PatientWithUser(**patient_dict)

@router.post("/", response_model=patient_schemas.PatientWithUser, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: patient_schemas.PatientCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient."""
    # Check if email already exists
    if db.query(models.User).filter(models.User.email == patient_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = models.User(
        email=patient_data.email,
        hashed_password=get_password_hash(patient_data.password),
        full_name=patient_data.full_name,
        role=models.UserRole.PATIENT,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create patient profile
    patient = models.Patient(
        user_id=user.id,
        date_of_birth=patient_data.date_of_birth,
        medical_history=patient_data.medical_history
    )
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    # Return combined patient and user information
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "date_of_birth": patient.date_of_birth,
        "medical_history": patient.medical_history,
        "created_at": patient.created_at,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    }
    
    return patient_schemas.PatientWithUser(**patient_dict)

@router.put("/{patient_id}", response_model=patient_schemas.PatientWithUser)
async def update_patient(
    patient_id: int,
    patient_data: patient_schemas.PatientUpdate,
    db: Session = Depends(get_db)
):
    """Update a patient."""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update patient fields
    for key, value in patient_data.dict(exclude_unset=True).items():
        if key == "is_active":
            # Update user.is_active
            patient.user.is_active = value
        else:
            # Update patient fields
            setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    
    # Return updated patient
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "date_of_birth": patient.date_of_birth,
        "medical_history": patient.medical_history,
        "created_at": patient.created_at,
        "email": patient.user.email,
        "full_name": patient.user.full_name,
        "is_active": patient.user.is_active
    }
    
    return patient_schemas.PatientWithUser(**patient_dict)