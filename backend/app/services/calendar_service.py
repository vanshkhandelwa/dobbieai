from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from datetime import datetime
import os
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.db import models
from app.core.config import settings

class CalendarService:
    def create_calendar_event(
        self, 
        db: Session, 
        appointment_id: int, 
        doctor_id: int, 
        patient_id: int, 
        start_time: datetime, 
        end_time: datetime,
        reason: Optional[str] = None
    ) -> Optional[str]:
        """Create a calendar event for an appointment and return the event ID."""
        try:
            # Get doctor and patient information
            doctor = db.query(models.Doctor).join(models.User).filter(
                models.Doctor.id == doctor_id
            ).first()
            
            patient = db.query(models.Patient).join(models.User).filter(
                models.Patient.id == patient_id
            ).first()
            
            if not doctor or not patient:
                raise HTTPException(status_code=404, detail="Doctor or patient not found")
                
            # Get doctor's calendar ID
            calendar_id = doctor.calendar_id or 'primary'
            
            # Get doctor's credentials
            # In a real application, you would store and retrieve OAuth tokens
            # Here we're using a simplified approach
            credentials = self._get_google_credentials(doctor_id)
            
            if not credentials:
                # Fall back to service account if user credentials not available
                return self._create_event_with_service_account(
                    calendar_id, 
                    doctor.user.full_name,
                    patient.user.full_name,
                    start_time,
                    end_time,
                    reason
                )
            
            # Create Calendar API service
            service = build('calendar', 'v3', credentials=credentials)
            
            # Create event
            event = {
                'summary': f'Appointment with {patient.user.full_name}',
                'description': reason or 'Medical appointment',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': doctor.user.email},
                    {'email': patient.user.email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            return event.get('id')
            
        except HttpError as error:
            # Handle Google API errors
            print(f"Google Calendar API Error: {error}")
            return None
            
        except Exception as e:
            # Handle other errors
            print(f"Error creating calendar event: {e}")
            return None
    
    def _create_event_with_service_account(
        self,
        calendar_id: str,
        doctor_name: str,
        patient_name: str,
        start_time: datetime,
        end_time: datetime,
        reason: Optional[str]
    ) -> Optional[str]:
        """Create a calendar event using a service account."""
        # In a real application, you would use a service account
        # For this demo, we'll simulate success
        print(f"Creating calendar event with service account: {doctor_name} with {patient_name}")
        # Return a mock event ID
        return f"mock_event_{int(datetime.now().timestamp())}"
    
    def _get_google_credentials(self, doctor_id: int) -> Optional[Credentials]:
        """Get Google OAuth credentials for a doctor."""
        # In a real application, you would store and retrieve tokens in a secure manner
        # For this demo, we'll return None to simulate using a service account instead
        return None