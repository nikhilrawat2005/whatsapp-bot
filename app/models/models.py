from datetime import datetime
from app.database.db import db


# ─────────────────────────────────────────────
#  Core Appointment Models (existing, extended)
# ─────────────────────────────────────────────

class Patient(db.Model):
    __tablename__ = 'patients'

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    age            = db.Column(db.Integer, nullable=False)
    gender         = db.Column(db.String(20), nullable=False)
    problem        = db.Column(db.Text)
    doctor         = db.Column(db.String(100), nullable=False)
    department     = db.Column(db.String(100))                          # NEW
    booking_date   = db.Column(db.String(20), nullable=False)           # YYYY-MM-DD
    booking_time   = db.Column(db.String(20), nullable=False)           # HH:MM
    phone_number   = db.Column(db.String(20), nullable=False)
    email          = db.Column(db.String(150))                          # NEW
    booking_status = db.Column(db.String(20), nullable=False,
                               default='Scheduled')                     # Scheduled|Confirmed|Completed|Cancelled
    notes          = db.Column(db.Text)                                 # NEW – admin notes
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    chat_messages  = db.relationship('ChatMessage', backref='patient',
                                     lazy=True, foreign_keys='ChatMessage.patient_id')


class AvailableSlot(db.Model):
    __tablename__ = 'available_slots'

    id         = db.Column(db.Integer, primary_key=True)
    doctor     = db.Column(db.String(100), nullable=False)
    date       = db.Column(db.String(20), nullable=False)               # YYYY-MM-DD
    time       = db.Column(db.String(20), nullable=False)               # HH:MM
    is_booked  = db.Column(db.Integer, nullable=False, default=0)       # 0 = free, 1 = booked
    patient_id = db.Column(db.Integer,
                           db.ForeignKey('patients.id', ondelete='SET NULL'),
                           nullable=True)

    __table_args__ = (
        db.UniqueConstraint('doctor', 'date', 'time', name='_doctor_slot_uc'),
    )


# BotState model removed because WhatsApp Bot integrations are disabled.


# ─────────────────────────────────────────────
#  Web Chat Session (NEW)
# ─────────────────────────────────────────────

class WebChatSession(db.Model):
    """Tracks state for the browser-based AI chat widget (mirrors BotState for web)."""
    __tablename__ = 'web_chat_sessions'

    id           = db.Column(db.Integer, primary_key=True)
    session_key  = db.Column(db.String(64), unique=True, nullable=False, index=True)
    state        = db.Column(db.String(50), nullable=False, default='WELCOME')

    # Temp booking data collected during chat
    temp_name    = db.Column(db.String(100))
    temp_age     = db.Column(db.Integer)
    temp_gender  = db.Column(db.String(20))
    temp_problem = db.Column(db.Text)
    temp_phone   = db.Column(db.String(20))
    temp_email   = db.Column(db.String(150))
    temp_dept    = db.Column(db.String(100))
    temp_doctor  = db.Column(db.String(100))
    temp_date    = db.Column(db.String(20))
    temp_slot    = db.Column(db.String(20))

    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow)

    messages     = db.relationship('ChatMessage', backref='session',
                                   lazy=True, foreign_keys='ChatMessage.session_id',
                                   order_by='ChatMessage.timestamp')


# ─────────────────────────────────────────────
#  Chat Message History (NEW)
# ─────────────────────────────────────────────

class ChatMessage(db.Model):
    """Stores individual chat messages for both web and WhatsApp conversations."""
    __tablename__ = 'chat_messages'

    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer,
                           db.ForeignKey('web_chat_sessions.id', ondelete='CASCADE'),
                           nullable=True)
    patient_id = db.Column(db.Integer,
                           db.ForeignKey('patients.id', ondelete='SET NULL'),
                           nullable=True)
    sender     = db.Column(db.String(10), nullable=False)              # 'user' or 'bot'
    message    = db.Column(db.Text, nullable=False)
    channel    = db.Column(db.String(20), default='web')               # web | whatsapp
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
#  Hospital Settings (NEW)
# ─────────────────────────────────────────────

class HospitalSettings(db.Model):
    """Key-value store for dynamic hospital configuration."""
    __tablename__ = 'hospital_settings'

    id    = db.Column(db.Integer, primary_key=True)
    key   = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)

    @classmethod
    def get(cls, key, default=None):
        """Fetch setting value by key with optional default."""
        record = cls.query.filter_by(key=key).first()
        return record.value if record else default

    @classmethod
    def set(cls, key, value):
        """Upsert a setting value."""
        record = cls.query.filter_by(key=key).first()
        if record:
            record.value = value
        else:
            record = cls(key=key, value=value)
            db.session.add(record)


# ─────────────────────────────────────────────
#  Doctor Profiles (NEW)
# ─────────────────────────────────────────────

class Doctor(db.Model):
    """Doctor profiles linked to departments."""
    __tablename__ = 'doctors'

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    department     = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(200))
    bio            = db.Column(db.Text)
    available      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
