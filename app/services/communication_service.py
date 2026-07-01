"""
Communication Service — Modular Notification Layer
===================================================
All outbound notifications pass through this service.
Business logic never calls WhatsApp / Email / SMS directly.

Current channels:  web (log only)
Future channels:   whatsapp, telegram, email, sms

To add a new channel:
    1. Add a handler function  _send_<channel>(patient, template, **ctx)
    2. Register it in CHANNEL_HANDLERS dict
    3. Call notify_*() with channel='<channel>'
"""

import logging
from app.config import Config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Internal channel handlers
# ─────────────────────────────────────────────

def _send_web(patient_or_dict, template: str, **ctx):
    """Web channel: logs the notification (UI shows status in admin)."""
    name = getattr(patient_or_dict, 'name', patient_or_dict.get('name', 'Patient'))
    logger.info(f"[WEB NOTIFY] {template} → {name}")


def _send_whatsapp(patient_or_dict, template: str, **ctx):
    """WhatsApp channel: stub — logs the notification."""
    phone = getattr(patient_or_dict, 'phone_number',
                    patient_or_dict.get('phone_number', ''))
    logger.info(f"[WHATSAPP STUB] Would send to {phone}: {template[:60]}")


def _send_email(patient_or_dict, template: str, **ctx):
    """Email channel: stub — connect SMTP / SendGrid here."""
    email = getattr(patient_or_dict, 'email', patient_or_dict.get('email', ''))
    logger.info(f"[EMAIL STUB] Would send to {email}: {template[:60]}")


def _send_sms(patient_or_dict, template: str, **ctx):
    """SMS channel: stub — connect Twilio / Fast2SMS here."""
    phone = getattr(patient_or_dict, 'phone_number',
                    patient_or_dict.get('phone_number', ''))
    logger.info(f"[SMS STUB] Would send to {phone}: {template[:60]}")


def _send_telegram(patient_or_dict, template: str, **ctx):
    """Telegram channel: stub — connect Telegram Bot API here."""
    logger.info(f"[TELEGRAM STUB] {template[:60]}")


CHANNEL_HANDLERS = {
    'web':       _send_web,
    'whatsapp':  _send_whatsapp,
    'email':     _send_email,
    'sms':       _send_sms,
    'telegram':  _send_telegram,
}


# ─────────────────────────────────────────────
#  Message templates
# ─────────────────────────────────────────────

def _confirmed_msg(patient) -> str:
    name  = getattr(patient, 'name', patient.get('name', 'Patient'))
    doc   = getattr(patient, 'doctor', patient.get('doctor', ''))
    date  = getattr(patient, 'booking_date', patient.get('booking_date', ''))
    time  = getattr(patient, 'booking_time', patient.get('booking_time', ''))
    return (
        f"✅ Appointment Confirmed!\n\n"
        f"Hello {name}, your appointment is confirmed.\n"
        f"👨‍⚕️ Doctor: {doc}\n📅 Date: {date}\n⏰ Time: {time}\n\n"
        f"Please arrive 10 minutes early. — {Config.HOSPITAL_NAME}"
    )


def _cancelled_msg(patient) -> str:
    name = getattr(patient, 'name', patient.get('name', 'Patient'))
    return (
        f"❌ Appointment Cancelled\n\n"
        f"Hello {name}, your appointment has been cancelled.\n"
        f"To rebook, visit our website or contact {Config.HOSPITAL_PHONE}."
    )


def _reminder_msg(patient) -> str:
    name = getattr(patient, 'name', patient.get('name', 'Patient'))
    doc  = getattr(patient, 'doctor', patient.get('doctor', ''))
    date = getattr(patient, 'booking_date', patient.get('booking_date', ''))
    time = getattr(patient, 'booking_time', patient.get('booking_time', ''))
    return (
        f"⏰ Appointment Reminder\n\n"
        f"Hi {name}, this is a reminder for your appointment tomorrow.\n"
        f"👨‍⚕️ {doc} | 📅 {date} | ⏰ {time}\n\n— {Config.HOSPITAL_NAME}"
    )


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def _dispatch(patient, template_fn, channel='web'):
    """Internal dispatcher — routes notification to correct channel handler."""
    message = template_fn(patient)
    handler = CHANNEL_HANDLERS.get(channel, _send_web)
    try:
        handler(patient, message)
    except Exception as e:
        logger.error(f"Notification dispatch error [{channel}]: {e}")


def notify_appointment_confirmed(patient, channel='web'):
    """Send appointment confirmation notification."""
    _dispatch(patient, _confirmed_msg, channel)


def notify_appointment_cancelled(patient, channel='web'):
    """Send appointment cancellation notification."""
    _dispatch(patient, _cancelled_msg, channel)


def notify_appointment_reminder(patient, channel='web'):
    """Send appointment reminder notification (call from scheduler)."""
    _dispatch(patient, _reminder_msg, channel)
