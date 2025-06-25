from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from mcp import MCPHost, MCPServer, FastAPITransport, tool
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.db.database import get_db
from app.services.appointment_service import AppointmentService
from app.services.calendar_service import CalendarService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
from app.schemas.appointment import DoctorAvailability, AvailabilitySlot, AppointmentCreate
from app.schemas.report import ReportRequest, DoctorReport

class MCPAppointmentServer:
    def __init__(self, app: FastAPI):
        self.app = app
        self.appointment_service = AppointmentService()
        self.calendar_service = CalendarService()
        self.email_service = EmailService()
        self.notification_service = NotificationService()
        
        # Set up MCP host and server
        self.mcp_host = MCPHost()
        self.mcp_server = MCPServer(
            host=self.mcp_host,
            transport=FastAPITransport(app=app, path="/mcp"),
            title="Doctor Appointment Assistant",
            description="MCP server for doctor appointments and reporting"
        )
        
        # Register tools
        self.register_tools()
    
    def register_tools(self):
        # Register all tools with the MCP server
        
        @self.mcp_server.tool("check_doctor_availability")
        async def check_doctor_availability(
            doctor_name: str,
            date: Optional[str] = None,
            time_of_day: Optional[str] = None,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """
            Check a doctor's availability for a specific date and time of day.
            
            Args:
                doctor_name: Full name of the doctor
                date: Date in YYYY-MM-DD format or natural language like "tomorrow", "Friday"
                time_of_day: Time preference like "morning", "afternoon", "evening", or specific time
                
            Returns:
                Availability information with possible slots
            """
            try:
                results = self.appointment_service.check_doctor_availability(
                    db, doctor_name, date, time_of_day
                )
                
                available_slots = []
                for result in results:
                    for slot in result.available_slots:
                        available_slots.append({
                            "start_time": slot.start_time.isoformat(),
                            "end_time": slot.end_time.isoformat()
                        })
                
                return {
                    "doctor_id": results[0].doctor_id if results else None,
                    "doctor_name": doctor_name,
                    "has_availability": len(available_slots) > 0,
                    "available_slots": available_slots,
                    "message": f"Found {len(available_slots)} available slots"
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "doctor_name": doctor_name,
                    "has_availability": False,
                    "available_slots": [],
                    "message": f"Error checking availability: {str(e)}"
                }
                
        @self.mcp_server.tool("schedule_appointment")
        async def schedule_appointment(
            doctor_id: int,
            patient_id: int,
            appointment_time: str,
            duration_minutes: int = 30,
            reason: Optional[str] = None,
            symptoms: Optional[str] = None,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """
            Schedule an appointment with a doctor.
            
            Args:
                doctor_id: ID of the doctor
                patient_id: ID of the patient
                appointment_time: ISO format datetime string for appointment
                duration_minutes: Duration of appointment in minutes
                reason: Reason for the appointment
                symptoms: Patient's symptoms
                
            Returns:
                Appointment details
            """
            try:
                start_time = datetime.fromisoformat(appointment_time)
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                appointment_data = AppointmentCreate(
                    doctor_id=doctor_id,
                    patient_id=patient_id,
                    appointment_time=start_time,
                    end_time=end_time,
                    reason=reason,
                    symptoms=symptoms
                )
                
                # Create appointment and add to calendar
                appointment = self.appointment_service.create_appointment(db, appointment_data)
                
                # Add to Google Calendar
                calendar_event_id = self.calendar_service.create_calendar_event(
                    db, appointment.id, doctor_id, patient_id, start_time, end_time, reason
                )
                
                # Update appointment with calendar event ID
                if calendar_event_id:
                    self.appointment_service.update_appointment_calendar_id(
                        db, appointment.id, calendar_event_id
                    )
                
                # Send email confirmation
                self.email_service.send_appointment_confirmation(
                    db, appointment.id, doctor_id, patient_id
                )
                
                return {
                    "appointment_id": appointment.id,
                    "doctor_id": doctor_id,
                    "patient_id": patient_id,
                    "appointment_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "status": appointment.status,
                    "calendar_event_id": calendar_event_id,
                    "success": True,
                    "message": "Appointment scheduled successfully"
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to schedule appointment: {str(e)}"
                }

        @self.mcp_server.tool("get_doctor_report")
        async def get_doctor_report(
            doctor_id: int,
            date_from: Optional[str] = None,
            date_to: Optional[str] = None,
            condition: Optional[str] = None,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """
            Get a summary report for a doctor's appointments.
            
            Args:
                doctor_id: ID of the doctor
                date_from: Optional start date in YYYY-MM-DD format or natural language
                date_to: Optional end date in YYYY-MM-DD format or natural language
                condition: Optional medical condition to filter by
                
            Returns:
                Doctor report summary
            """
            try:
                # Create report request
                request = ReportRequest(
                    doctor_id=doctor_id,
                    date_from=datetime.fromisoformat(date_from).date() if date_from else None,
                    date_to=datetime.fromisoformat(date_to).date() if date_to else None,
                    condition=condition
                )
                
                # Generate report
                report = self.appointment_service.generate_doctor_report(db, request)
                
                # Send notification
                self.notification_service.send_report_notification(db, doctor_id, report)
                
                result = {
                    "doctor_id": report.doctor_id,
                    "doctor_name": report.doctor_name,
                    "report_date": report.report_date.isoformat(),
                    "appointment_stats": {
                        "total": report.appointment_stats.total,
                        "completed": report.appointment_stats.completed,
                        "scheduled": report.appointment_stats.scheduled,
                        "cancelled": report.appointment_stats.cancelled
                    },
                    "summary": report.summary
                }
                
                if report.daily_breakdown:
                    result["daily_breakdown"] = [
                        {"date": item.date.isoformat(), "count": item.count}
                        for item in report.daily_breakdown
                    ]
                    
                if report.common_conditions:
                    result["common_conditions"] = [
                        {"condition": item.condition, "count": item.count}
                        for item in report.common_conditions
                    ]
                
                return result
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to generate report: {str(e)}"
                }

        # Add more tools as needed...