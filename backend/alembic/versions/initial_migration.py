"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-06-24 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types first
    op.execute('CREATE TYPE userrole AS ENUM (\'doctor\', \'patient\')')
    op.execute('CREATE TYPE appointmentstatus AS ENUM (\'scheduled\', \'completed\', \'cancelled\')')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('doctor', 'patient', name='userrole', native_enum=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Create doctors table
    op.create_table('doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('calendar_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_doctors_id'), 'doctors', ['id'], unique=False)
    
    # Create patients table
    op.create_table('patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date_of_birth', sa.DateTime(), nullable=True),
        sa.Column('medical_history', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    
    # Create availabilities table
    op.create_table('availabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),  # 0 = Monday, 6 = Sunday
        sa.Column('start_time', sa.String(), nullable=False),    # Format: "HH:MM"
        sa.Column('end_time', sa.String(), nullable=False),      # Format: "HH:MM"
        sa.Column('is_available', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_availabilities_id'), 'availabilities', ['id'], unique=False)
    
    # Create appointments table
    op.create_table('appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('scheduled', 'completed', 'cancelled', name='appointmentstatus', native_enum=True), 
                  nullable=False, server_default='scheduled'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('symptoms', sa.Text(), nullable=True),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('calendar_event_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_id'), 'appointments', ['id'], unique=False)


def downgrade():
    op.drop_table('appointments')
    op.drop_table('availabilities')
    op.drop_table('patients')
    op.drop_table('doctors')
    op.drop_table('users')
    op.execute('DROP TYPE appointmentstatus')
    op.execute('DROP TYPE userrole')