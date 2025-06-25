from sqlalchemy.orm import Session
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

from app.db import models
from app.core.config import settings

class EmailService:
    def send_appointment_confirmation(
        self,
        db: Session,
        appointment_id: int,
        doctor_id: int,
        patient_id: int
    ) -> bool:
        """Send an email confirmation for an appointment."""
        try:
            # Get appointment, doctor and patient information
            appointment = db.query(models.Appointment).filter(
                models.Appointment.id == appointment_id
            ).first()
            
            doctor = db.query(models.Doctor).join(models.User).filter(
                models.Doctor.id == doctor_id
            ).first()
            
            patient = db.query(models.Patient).join(models.User).filter(
                models.Patient.id == patient_id
            ).first()
            
            if not appointment or not doctor or not patient:
                raise HTTPException(status_code=404, detail="Appointment, doctor or patient not found")
                
            # Prepare email content
            subject = f"Appointment Confirmation with Dr. {doctor.user.full_name}"
            
            # Format appointment date and time
            formatted_date = appointment.appointment_time.strftime("%A, %B %d, %Y")
            formatted_start_time = appointment.appointment_time.strftime("%I:%M %p")
            formatted_end_time = appointment.end_time.strftime("%I:%M %p")
            
            # Create email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>Appointment Confirmation</h2>
                <p>Dear {patient.user.full_name},</p>
                
                <p>Your appointment with <b>Dr. {doctor.user.full_name}</b> has been confirmed for:</p>
                
                <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #4285f4; border-radius: 4px;">
                    <p><b>Date:</b> {formatted_date}<br>
                    <b>Time:</b> {formatted_start_time} - {formatted_end_time}</p>
                </div>
                
                <p><b>Reason for visit:</b> {appointment.reason or 'Not specified'}</p>
                
                <h3>Important Information:</h3>
                <ul>
                    <li>Please arrive 15 minutes before your appointment time.</li>
                    <li>Bring your insurance card and ID.</li>
                    <li>If you need to cancel or reschedule, please contact us at least 24 hours in advance.</li>
                </ul>
                
                <p>If you have any questions, please don't hesitate to contact us.</p>
                
                <p>Best regards,<br>
                Medical Staff</p>
            </body>
            </html>
            """
            
            # Send email
            self._send_email(patient.user.email, subject, body)
            
            return True
            
        except Exception as e:
            # Handle errors
            print(f"Error sending appointment confirmation email: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, body: str) -> None:
        """Send an email using SMTP."""
        # If we're in development mode, just print the email
        if not settings.EMAIL_SENDER or not settings.EMAIL_PASSWORD:
            print("\n--- EMAIL WOULD BE SENT ---")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print("--- END EMAIL ---\n")
            return
            
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.EMAIL_SENDER
        message["To"] = to_email
        
        # Attach HTML body
        html_part = MIMEText(body, "html")
        message.attach(html_part)
        
        # Send email
        try:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
                server.sendmail(settings.EMAIL_SENDER, to_email, message.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")
            raise e