from datetime import datetime
from app.database.db import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    problem = db.Column(db.Text)
    doctor = db.Column(db.String(100), nullable=False)
    booking_date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    booking_time = db.Column(db.String(20), nullable=False) # HH:MM
    phone_number = db.Column(db.String(20), nullable=False)
    booking_status = db.Column(db.String(20), nullable=False, default='Scheduled') # Scheduled, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AvailableSlot(db.Model):
    __tablename__ = 'available_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    time = db.Column(db.String(20), nullable=False) # HH:MM
    is_booked = db.Column(db.Integer, nullable=False, default=0) # 0 for false, 1 for true
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='SET NULL'), nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('doctor', 'date', 'time', name='_doctor_slot_uc'),
    )

class BotState(db.Model):
    __tablename__ = 'bot_states'
    
    phone_number = db.Column(db.String(20), primary_key=True)
    state = db.Column(db.String(50), nullable=False, default='WELCOME')
    temp_name = db.Column(db.String(100))
    temp_age = db.Column(db.Integer)
    temp_gender = db.Column(db.String(20))
    temp_problem = db.Column(db.Text)
    temp_doctor = db.Column(db.String(100))
    temp_date = db.Column(db.String(20))
    temp_slot = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
