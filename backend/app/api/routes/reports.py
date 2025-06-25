from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db.database import get_db
from app.services.appointment_service import AppointmentService
from app.services.notification_service import NotificationService
from app.schemas import report as report_schemas

router = APIRouter(prefix="/reports", tags=["reports"])

appointment_service = AppointmentService()
notification_service = NotificationService()

@router.post("/doctor-report", response_model=report_schemas.DoctorReport)
async def generate_doctor_report(
    request: report_schemas.ReportRequest,
    db: Session = Depends(get_db)
):
    """Generate a report for a doctor."""
    try:
        # Generate the report
        report = appointment_service.generate_doctor_report(db, request)
        
        # Send notification with the report
        notification_service.send_report_notification(db, request.doctor_id, report)
        
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

@router.get("/stats/doctor/{doctor_id}", response_model=report_schemas.AppointmentStats)
async def get_doctor_appointment_stats(
    doctor_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get appointment statistics for a doctor."""
    try:
        # Create report request
        request = report_schemas.ReportRequest(
            doctor_id=doctor_id,
            date_from=from_date,
            date_to=to_date
        )
        
        # Generate report
        report = appointment_service.generate_doctor_report(db, request)
        
        # Return just the stats
        return report.appointment_stats
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get appointment statistics: {str(e)}"
        )