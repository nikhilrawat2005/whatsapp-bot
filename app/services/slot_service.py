import datetime
import logging
from sqlalchemy.exc import IntegrityError
from app.database.db import db
from app.models.models import AvailableSlot, Patient

logger = logging.getLogger(__name__)

DOCTORS_LIST = [
    "General Physician",
    "Dentist",
    "Orthopedic",
    "Cardiologist",
    "Dermatologist"
]

def generate_slots_for_next_30_days():
    """Generates available slots for all doctors for the next 30 days.
    Slots are 9:00 AM to 5:00 PM, every 30 minutes, excluding lunch (1 PM - 2 PM).
    Uses database upserts/ignores to preserve existing slots.
    """
    start_date = datetime.date.today()
    slots_inserted = 0
    
    # Pre-populate slots list
    for day_offset in range(30):
        current_date = start_date + datetime.timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Define available times
        # 9:00 AM to 1:00 PM
        morning_times = []
        hour = 9
        minute = 0
        while hour < 13:
            morning_times.append(f"{hour:02d}:{minute:02d}")
            minute += 30
            if minute == 60:
                hour += 1
                minute = 0
                
        # 2:00 PM to 5:00 PM (Ends at 5:00 PM, meaning last slot starts at 4:30 PM)
        afternoon_times = []
        hour = 14
        minute = 0
        while hour < 17:
            afternoon_times.append(f"{hour:02d}:{minute:02d}")
            minute += 30
            if minute == 60:
                hour += 1
                minute = 0
                
        all_times = morning_times + afternoon_times
        
        for doctor in DOCTORS_LIST:
            for t_str in all_times:
                # Check duplicate slot presence before inserting to prevent unique constraint crashes
                existing = AvailableSlot.query.filter_by(doctor=doctor, date=date_str, time=t_str).first()
                if not existing:
                    slot = AvailableSlot(
                        doctor=doctor,
                        date=date_str,
                        time=t_str,
                        is_booked=0,
                        patient_id=None
                    )
                    db.session.add(slot)
                    slots_inserted += 1
                    
    try:
        db.session.commit()
        if slots_inserted > 0:
            logger.info(f"Successfully generated {slots_inserted} available appointment slots.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error executing slot generation: {e}")
        
    return slots_inserted

def get_available_dates(doctor):
    """Returns unique future dates where the doctor has at least one unbooked slot."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # Query distinct dates
    results = db.session.query(AvailableSlot.date).filter(
        AvailableSlot.doctor == doctor,
        AvailableSlot.date >= today_str,
        AvailableSlot.is_booked == 0
    ).distinct().order_by(AvailableSlot.date.asc()).limit(5).all()
    
    return [r[0] for r in results]

def get_available_slots(doctor, date_str):
    """Returns available times for a specific doctor on a specific date."""
    results = AvailableSlot.query.filter_by(
        doctor=doctor,
        date=date_str,
        is_booked=0
    ).order_by(AvailableSlot.time.asc()).all()
    
    return [r.time for r in results]

def book_appointment_transaction(phone_number, name, age, gender, problem, doctor, date_str, time_str):
    """Transactionally attempts to book the selected slot for the patient.
    Uses SQLAlchemy locking (with_for_update) to prevent race conditions.
    """
    try:
        # 1. Fetch slot with write-lock (preventing concurrent reads/writes)
        slot = AvailableSlot.query.filter_by(
            doctor=doctor,
            date=date_str,
            time=time_str
        ).with_for_update().first()
        
        if not slot:
            return False, "Selected slot does not exist."
            
        if slot.is_booked == 1:
            return False, "This slot has already been booked by another patient."
            
        # 2. Record Patient entry
        patient = Patient(
            name=name,
            age=age,
            gender=gender,
            problem=problem,
            doctor=doctor,
            booking_date=date_str,
            booking_time=time_str,
            phone_number=phone_number,
            booking_status='Scheduled'
        )
        db.session.add(patient)
        db.session.flush() # Populate patient.id without committing
        
        # 3. Associate patient to slot
        slot.is_booked = 1
        slot.patient_id = patient.id
        
        db.session.commit()
        logger.info(f"Booked appointment ID {patient.id} for {name} on {date_str} {time_str}")
        return True, "Appointment booked successfully!"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed transaction while booking appointment: {e}")
        return False, f"Database transaction error: {str(e)}"

def release_appointment_slot(patient_id):
    """Releases a booked slot and marks the patient record as Cancelled."""
    try:
        patient = Patient.query.filter_by(id=patient_id).with_for_update().first()
        if patient:
            patient.booking_status = 'Cancelled'
            
            # Find and free corresponding slot
            slot = AvailableSlot.query.filter_by(
                doctor=patient.doctor,
                date=patient.booking_date,
                time=patient.booking_time
            ).with_for_update().first()
            
            if slot:
                slot.is_booked = 0
                slot.patient_id = None
                
            db.session.commit()
            logger.info(f"Released and cancelled appointment ID {patient_id}")
            return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error releasing slot: {e}")
        return False
    return False
