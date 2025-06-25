from sqlalchemy.orm import Session
import requests
from datetime import datetime
import json

from app.db import models
from app.schemas import report as report_schemas
from app.core.config import settings

class NotificationService:
    def send_report_notification(
        self,
        db: Session,
        doctor_id: int,
        report: report_schemas.DoctorReport
    ) -> bool:
        """Send a notification with a doctor report."""
        try:
            # Get doctor information
            doctor = db.query(models.Doctor).join(models.User).filter(
                models.Doctor.id == doctor_id
            ).first()
            
            if not doctor:
                return False
                
            # Format notification message
            message = self._format_report_notification(doctor.user.full_name, report)
            
            # Send notification via Slack or other service
            if settings.SLACK_WEBHOOK_URL:
                return self._send_slack_notification(message)
            else:
                # Fallback to console for development
                print("\n--- NOTIFICATION WOULD BE SENT ---")
                print(message)
                print("--- END NOTIFICATION ---\n")
                return True
                
        except Exception as e:
            # Handle errors
            print(f"Error sending report notification: {e}")
            return False
    
    def _format_report_notification(
        self,
        doctor_name: str,
        report: report_schemas.DoctorReport
    ) -> str:
        """Format a report notification message."""
        stats = report.appointment_stats
        
        # Format date range
        date_range = "Last 7 days"  # Default
        if report.daily_breakdown and len(report.daily_breakdown) > 0:
            first_date = min(day.date for day in report.daily_breakdown)
            last_date = max(day.date for day in report.daily_breakdown)
            date_range = f"{first_date.strftime('%b %d')} to {last_date.strftime('%b %d, %Y')}"
        
        # Build message
        message = f"*Doctor Report for Dr. {doctor_name}*\n"
        message += f"*Period:* {date_range}\n\n"
        
        # Appointment stats
        message += "*Appointment Summary:*\n"
        message += f"• Total: {stats.total}\n"
        message += f"• Completed: {stats.completed}\n"
        message += f"• Scheduled: {stats.scheduled}\n"
        message += f"• Cancelled: {stats.cancelled}\n\n"
        
        # Common conditions
        if report.common_conditions and len(report.common_conditions) > 0:
            message += "*Top Conditions:*\n"
            for condition in report.common_conditions[:3]:  # Show top 3
                message += f"• {condition.condition.title()}: {condition.count}\n"
            message += "\n"
        
        # Add summary
        message += "*Summary:*\n"
        message += report.summary
        
        return message
    
    def _send_slack_notification(self, message: str) -> bool:
        """Send a notification via Slack webhook."""
        try:
            payload = {
                "text": message
            }
            
            response = requests.post(
                settings.SLACK_WEBHOOK_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False