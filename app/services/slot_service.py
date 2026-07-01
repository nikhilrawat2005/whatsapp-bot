import datetime
import logging
from sqlalchemy.exc import IntegrityError
from app.database.db import db
from app.models.models import AvailableSlot, Patient

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  Master Data — Departments & Doctors
# ─────────────────────────────────────────────

DEPARTMENTS = {
    "General Medicine": {
        "icon": "🩺",
        "doctors": ["Dr. Arjun Mehta", "Dr. Priya Sharma"],
        "description": "Primary care and general health consultations"
    },
    "Dentistry": {
        "icon": "🦷",
        "doctors": ["Dr. Kavita Nair"],
        "description": "Complete oral health, dental surgery and aesthetics"
    },
    "Orthopedics": {
        "icon": "🦴",
        "doctors": ["Dr. Rajesh Verma", "Dr. Suresh Patel"],
        "description": "Bone, joint, spine and muscular system specialists"
    },
    "Cardiology": {
        "icon": "❤️",
        "doctors": ["Dr. Anita Gupta"],
        "description": "Heart and cardiovascular health consultants"
    },
    "Dermatology": {
        "icon": "🌿",
        "doctors": ["Dr. Meera Joshi"],
        "description": "Advanced care for skin, hair, and nail conditions"
    },
}

# Flat list of all doctors (for backward compatibility with existing bot)
DOCTORS_LIST = [doc for dept in DEPARTMENTS.values() for doc in dept["doctors"]]

# Legacy compatibility alias (slot_service previously had this name)
DEPARTMENTS_LIST = list(DEPARTMENTS.keys())

def get_doctor_department(doctor_name: str) -> str:
    """Returns the department for a given doctor name."""
    for dept, info in DEPARTMENTS.items():
        if doctor_name in info["doctors"]:
            return dept
    return "General Medicine"


# ─────────────────────────────────────────────
#  Slot Generation
# ─────────────────────────────────────────────

def generate_slots_for_next_30_days():
    """Generates available slots for all doctors for the next 30 days.
    Slots are 9:00 AM to 5:00 PM, every 30 minutes, excluding lunch (1 PM–2 PM).
    Uses duplicate checks to preserve existing booked slots safely.
    """
    start_date    = datetime.date.today()
    slots_inserted = 0

    for day_offset in range(30):
        current_date = start_date + datetime.timedelta(days=day_offset)
        date_str     = current_date.strftime("%Y-%m-%d")

        # Morning: 09:00 → 13:00
        morning_times = []
        hour, minute  = 9, 0
        while hour < 13:
            morning_times.append(f"{hour:02d}:{minute:02d}")
            minute += 30
            if minute == 60:
                hour  += 1
                minute = 0

        # Afternoon: 14:00 → 17:00
        afternoon_times = []
        hour, minute    = 14, 0
        while hour < 17:
            afternoon_times.append(f"{hour:02d}:{minute:02d}")
            minute += 30
            if minute == 60:
                hour  += 1
                minute = 0

        all_times = morning_times + afternoon_times

        for doctor in DOCTORS_LIST:
            for t_str in all_times:
                existing = AvailableSlot.query.filter_by(
                    doctor=doctor, date=date_str, time=t_str
                ).first()
                if not existing:
                    slot = AvailableSlot(
                        doctor=doctor, date=date_str,
                        time=t_str, is_booked=0, patient_id=None
                    )
                    db.session.add(slot)
                    slots_inserted += 1

    try:
        db.session.commit()
        if slots_inserted > 0:
            logger.info(f"Generated {slots_inserted} appointment slots.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Slot generation error: {e}")

    return slots_inserted


# ─────────────────────────────────────────────
#  Query Helpers
# ─────────────────────────────────────────────

def get_available_dates(doctor):
    """Returns unique future dates where the doctor has ≥1 unbooked slot (next 5)."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    results = db.session.query(AvailableSlot.date).filter(
        AvailableSlot.doctor == doctor,
        AvailableSlot.date   >= today_str,
        AvailableSlot.is_booked == 0
    ).distinct().order_by(AvailableSlot.date.asc()).limit(5).all()
    return [r[0] for r in results]


def get_available_slots(doctor, date_str):
    """Returns available time strings for a specific doctor on a specific date."""
    results = AvailableSlot.query.filter_by(
        doctor=doctor, date=date_str, is_booked=0
    ).order_by(AvailableSlot.time.asc()).all()
    return [r.time for r in results]


def get_slots_summary(date_str):
    """Returns slot counts per doctor for a given date (used by calendar API)."""
    slots = AvailableSlot.query.filter_by(date=date_str).all()
    summary = {}
    for s in slots:
        if s.doctor not in summary:
            summary[s.doctor] = {"total": 0, "booked": 0, "available": 0}
        summary[s.doctor]["total"] += 1
        if s.is_booked:
            summary[s.doctor]["booked"] += 1
        else:
            summary[s.doctor]["available"] += 1
    return summary


# ─────────────────────────────────────────────
#  Booking Transaction (existing, untouched logic)
# ─────────────────────────────────────────────

def book_appointment_transaction(phone_number, name, age, gender, problem,
                                  doctor, date_str, time_str,
                                  email=None, department=None):
    """Transactionally books the selected slot for the patient.
    Uses SQLAlchemy with_for_update() to prevent race conditions.
    """
    try:
        # 1. Lock slot row
        slot = AvailableSlot.query.filter_by(
            doctor=doctor, date=date_str, time=time_str
        ).with_for_update().first()

        if not slot:
            return False, "Selected slot does not exist."
        if slot.is_booked == 1:
            return False, "This slot has already been booked by another patient."

        # Resolve department if not provided
        if not department:
            department = get_doctor_department(doctor)

        # 2. Create patient record
        patient = Patient(
            name=name, age=age, gender=gender, problem=problem,
            doctor=doctor, department=department,
            booking_date=date_str, booking_time=time_str,
            phone_number=phone_number, email=email,
            booking_status='Scheduled'
        )
        db.session.add(patient)
        db.session.flush()  # Get patient.id before commit

        # 3. Mark slot as booked
        slot.is_booked  = 1
        slot.patient_id = patient.id

        db.session.commit()
        logger.info(f"Booked appointment ID {patient.id} for {name} on {date_str} {time_str}")
        return True, patient.id

    except Exception as e:
        db.session.rollback()
        logger.error(f"Booking transaction failed: {e}")
        return False, f"Database error: {str(e)}"


# ─────────────────────────────────────────────
#  Slot Release / Cancellation (existing, untouched)
# ─────────────────────────────────────────────

def release_appointment_slot(patient_id):
    """Releases a booked slot and marks the patient record as Cancelled."""
    try:
        patient = Patient.query.filter_by(id=patient_id).with_for_update().first()
        if patient:
            patient.booking_status = 'Cancelled'
            slot = AvailableSlot.query.filter_by(
                doctor=patient.doctor,
                date=patient.booking_date,
                time=patient.booking_time
            ).with_for_update().first()
            if slot:
                slot.is_booked  = 0
                slot.patient_id = None
            db.session.commit()
            logger.info(f"Released and cancelled appointment ID {patient_id}")
            return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error releasing slot: {e}")
    return False
