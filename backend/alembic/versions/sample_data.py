"""Sample Data

Revision ID: 002
Revises: 001
Create Date: 2025-06-24 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime, Text, Boolean, Enum
from datetime import datetime, timedelta
from app.core.security import get_password_hash

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Define tables for data insertion
    users = table('users',
        column('id', Integer),
        column('email', String),
        column('hashed_password', String),
        column('full_name', String),
        column('role', String),
        column('is_active', Boolean),
        column('created_at', DateTime)
    )
    
    doctors = table('doctors',
        column('id', Integer),
        column('user_id', Integer),
        column('specialization', String),
        column('calendar_id', String),
        column('created_at', DateTime)
    )
    
    patients = table('patients',
        column('id', Integer),
        column('user_id', Integer),
        column('date_of_birth', DateTime),
        column('medical_history', Text),
        column('created_at', DateTime)
    )
    
    availabilities = table('availabilities',
        column('id', Integer),
        column('doctor_id', Integer),
        column('day_of_week', Integer),
        column('start_time', String),
        column('end_time', String),
        column('is_available', Boolean)
    )
    
    appointments = table('appointments',
        column('id', Integer),
        column('doctor_id', Integer),
        column('patient_id', Integer),
        column('appointment_time', DateTime),
        column('end_time', DateTime),
        column('status', String),
        column('reason', Text),
        column('symptoms', Text),
        column('diagnosis', Text),
        column('created_at', DateTime),
        column('calendar_event_id', String)
    )
    
    # Insert sample doctors
    op.bulk_insert(users, [
        {
            'id': 1,
            'email': 'dr.ahuja@example.com',
            'hashed_password': get_password_hash('password123'),
            'full_name': 'Dr. Vikram Ahuja',
            'role': 'doctor',
            'is_active': True,
            'created_at': datetime.now()
        },
        {
            'id': 2,
            'email': 'dr.sharma@example.com',
            'hashed_password': get_password_hash('password123'),
            'full_name': 'Dr. Priya Sharma',
            'role': 'doctor',
            'is_active': True,
            'created_at': datetime.now()
        },
        {
            'id': 3,
            'email': 'dr.patel@example.com',
            'hashed_password': get_password_hash('password123'),
            'full_name': 'Dr. Raj Patel',
            'role': 'doctor',
            'is_active': True,
            'created_at': datetime.now()
        }
    ])
    
    op.bulk_insert(doctors, [
        {
            'id': 1,
            'user_id': 1,
            'specialization': 'Cardiologist',
            'calendar_id': 'dr-ahuja@gmail.com',
            'created_at': datetime.now()
        },
        {
            'id': 2,
            'user_id': 2,
            'specialization': 'Dermatologist',
            'calendar_id': 'dr-sharma@gmail.com',
            'created_at': datetime.now()
        },
        {
            'id': 3,
            'user_id': 3,
            'specialization': 'General Physician',
            'calendar_id': 'dr-patel@gmail.com',
            'created_at': datetime.now()
        }
    ])
    
    # Insert sample patients
    op.bulk_insert(users, [
        {
            'id': 4,
            'email': 'patient1@example.com',
            'hashed_password': get_password_hash('password123'),
            'full_name': 'Amit Kumar',
            'role': 'patient',
            'is_active': True,
            'created_at': datetime.now()
        },
        {
            'id': 5,
            'email': 'patient2@example.com',
            'hashed_password': get_password_hash('password123'),
            'full_name': 'Neha Singh',
            'role': 'patient',
            'is_active': True,
            'created_at': datetime.now()
        }
    ])
    
    op.bulk_insert(patients, [
        {
            'id': 1,
            'user_id': 4,
            'date_of_birth': datetime(1985, 5, 15),
            'medical_history': 'High blood pressure, allergic to penicillin',
            'created_at': datetime.now()
        },
        {
            'id': 2,
            'user_id': 5,
            'date_of_birth': datetime(1990, 8, 22),
            'medical_history': 'Asthma',
            'created_at': datetime.now()
        }
    ])
    
    # Insert doctor availabilities
    availabilities_data = []
    for doctor_id in [1, 2, 3]:
        for day in range(0, 5):  # Monday to Friday
            availabilities_data.append({
                'doctor_id': doctor_id,
                'day_of_week': day,
                'start_time': '09:00',
                'end_time': '17:00',
                'is_available': True
            })
    
    # Special availability for Dr. Ahuja on weekends
    availabilities_data.append({
        'doctor_id': 1,
        'day_of_week': 5,  # Saturday
        'start_time': '10:00',
        'end_time': '13:00',
        'is_available': True
    })
    
    op.bulk_insert(availabilities, availabilities_data)
    
    # Insert sample appointments
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    op.bulk_insert(appointments, [
        {
            'id': 1,
            'doctor_id': 1,
            'patient_id': 1,
            'appointment_time': yesterday.replace(hour=10, minute=0),
            'end_time': yesterday.replace(hour=10, minute=30),
            'status': 'completed',
            'reason': 'Regular checkup',
            'symptoms': 'Occasional chest pain',
            'diagnosis': 'Mild hypertension, prescribed medication',
            'created_at': yesterday - timedelta(days=2),
            'calendar_event_id': 'evt_123'
        },
        {
            'id': 2,
            'doctor_id': 1,
            'patient_id': 2,
            'appointment_time': today.replace(hour=14, minute=0),
            'end_time': today.replace(hour=14, minute=30),
            'status': 'scheduled',
            'reason': 'Heart palpitations',
            'symptoms': 'Palpitations, shortness of breath',
            'diagnosis': None,
            'created_at': yesterday,
            'calendar_event_id': 'evt_124'
        },
        {
            'id': 3,
            'doctor_id': 2,
            'patient_id': 1,
            'appointment_time': tomorrow.replace(hour=11, minute=0),
            'end_time': tomorrow.replace(hour=11, minute=30),
            'status': 'scheduled',
            'reason': 'Skin rash',
            'symptoms': 'Itchy red spots on arms',
            'diagnosis': None,
            'created_at': today - timedelta(days=1),
            'calendar_event_id': 'evt_125'
        },
        {
            'id': 4,
            'doctor_id': 3,
            'patient_id': 2,
            'appointment_time': yesterday.replace(hour=9, minute=0),
            'end_time': yesterday.replace(hour=9, minute=30),
            'status': 'completed',
            'reason': 'Fever',
            'symptoms': 'High temperature, headache',
            'diagnosis': 'Viral infection, rest recommended',
            'created_at': yesterday - timedelta(days=3),
            'calendar_event_id': 'evt_126'
        },
        {
            'id': 5,
            'doctor_id': 1,
            'patient_id': 1,
            'appointment_time': next_week.replace(hour=15, minute=0),
            'end_time': next_week.replace(hour=15, minute=30),
            'status': 'scheduled',
            'reason': 'Follow-up',
            'symptoms': None,
            'diagnosis': None,
            'created_at': today,
            'calendar_event_id': 'evt_127'
        }
    ])


def downgrade():
    # Delete sample data
    op.execute('DELETE FROM appointments')
    op.execute('DELETE FROM availabilities')
    op.execute('DELETE FROM patients')
    op.execute('DELETE FROM doctors')
    op.execute('DELETE FROM users')