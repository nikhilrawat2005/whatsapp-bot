"""
Web Chat Service
================
Conversational state engine for the browser-based AI chat widget.
Mirrors the WhatsApp BotState machine but runs on WebChatSession records.
All booking goes through the same slot_service booking functions — no duplicated logic.
"""

import datetime
import logging
from app.database.db import db
from app.models.models import WebChatSession, ChatMessage
from app.services import slot_service

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  Session helpers
# ─────────────────────────────────────────────

def get_or_create_session(session_key: str) -> WebChatSession:
    session = WebChatSession.query.filter_by(session_key=session_key).first()
    if not session:
        session = WebChatSession(session_key=session_key, state='WELCOME')
        db.session.add(session)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            session = WebChatSession.query.filter_by(session_key=session_key).first()
    return session


def _save_session(session: WebChatSession, updates: dict):
    for k, v in updates.items():
        setattr(session, k, v)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Session save error: {e}")


def _save_message(session: WebChatSession, sender: str, text: str):
    msg = ChatMessage(session_id=session.id, sender=sender, message=text, channel='web')
    db.session.add(msg)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Message save error: {e}")


# ─────────────────────────────────────────────
#  Response builder helpers
# ─────────────────────────────────────────────

def _resp(text, buttons=None, input_type='text', placeholder='Type your message…'):
    """Build a standard response dict."""
    return {
        'messages': [text] if isinstance(text, str) else text,
        'buttons':  buttons or [],
        'input':    {'type': input_type, 'placeholder': placeholder},
    }


def _multi(messages, buttons=None, input_type='text', placeholder='Type your message…'):
    return {
        'messages': messages,
        'buttons':  buttons or [],
        'input':    {'type': input_type, 'placeholder': placeholder},
    }


# ─────────────────────────────────────────────
#  Main handler
# ─────────────────────────────────────────────

def handle_web_message(session_key: str, message_text: str) -> dict:
    """
    Process one incoming message from the web chat widget.
    Returns a dict: {messages: [str], buttons: [str], input: {type, placeholder}}
    """
    msg     = message_text.strip()
    session = get_or_create_session(session_key)
    state   = session.state

    # Save user message
    _save_message(session, 'user', msg)

    # ── Global reset commands ──────────────────────────────────────────
    if msg.lower() in ['restart', 'start over', 'menu', 'home', '/start']:
        _save_session(session, {
            'state': 'WELCOME', 'temp_name': None, 'temp_age': None,
            'temp_gender': None, 'temp_problem': None, 'temp_phone': None,
            'temp_email': None, 'temp_dept': None, 'temp_doctor': None,
            'temp_date': None, 'temp_slot': None
        })
        response = _build_welcome(session)
        _save_message(session, 'bot', ' | '.join(response['messages']))
        return response

    # ── State routing ──────────────────────────────────────────────────
    handler_map = {
        'WELCOME':              _handle_welcome,
        'MAIN_MENU':            _handle_main_menu,
        'AWAITING_NAME':        _handle_name,
        'AWAITING_AGE':         _handle_age,
        'AWAITING_GENDER':      _handle_gender,
        'AWAITING_PHONE':       _handle_phone,
        'AWAITING_EMAIL':       _handle_email,
        'AWAITING_PROBLEM':     _handle_problem,
        'AWAITING_DEPT':        _handle_dept,
        'AWAITING_DOCTOR':      _handle_doctor,
        'AWAITING_DATE':        _handle_date,
        'AWAITING_SLOT':        _handle_slot,
        'AWAITING_CONFIRMATION': _handle_confirmation,
        'SHOW_DOCTORS':         _handle_show_doctors,
        'SHOW_DEPARTMENTS':     _handle_show_departments,
        'SHOW_INFO':            _handle_show_info,
        'CANCEL_FLOW':          _handle_cancel_flow,
    }

    handler  = handler_map.get(state, _handle_welcome)
    response = handler(session, msg)
    _save_message(session, 'bot', ' | '.join(response['messages']))
    return response


# ─────────────────────────────────────────────
#  State handlers
# ─────────────────────────────────────────────

def _build_welcome(session):
    hour = datetime.datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
    _save_session(session, {'state': 'MAIN_MENU'})
    return _resp(
        [f"{greeting}! 👋 Welcome to **ABC Hospital**.",
         "I'm your AI receptionist. How can I help you today?"],
        buttons=[
            "📅 Book Appointment",
            "👨‍⚕️ Our Doctors",
            "🏥 Departments",
            "📍 Hospital Info",
            "❌ Cancel Booking",
        ]
    )


def _handle_welcome(session, msg):
    return _build_welcome(session)


def _handle_main_menu(session, msg):
    m = msg.lower()
    if 'book' in m or 'appointment' in m:
        _save_session(session, {'state': 'AWAITING_NAME'})
        return _resp(
            "Great! Let's book your appointment. 📋\n\nFirst, please tell me your **full name**:",
            placeholder="Enter your full name"
        )
    elif 'doctor' in m:
        _save_session(session, {'state': 'SHOW_DOCTORS'})
        return _handle_show_doctors(session, msg)
    elif 'department' in m or 'dept' in m:
        _save_session(session, {'state': 'SHOW_DEPARTMENTS'})
        return _handle_show_departments(session, msg)
    elif 'info' in m or 'hospital' in m or 'location' in m or 'contact' in m:
        _save_session(session, {'state': 'SHOW_INFO'})
        return _handle_show_info(session, msg)
    elif 'cancel' in m:
        _save_session(session, {'state': 'CANCEL_FLOW'})
        return _resp(
            "To cancel an appointment, please provide your **phone number** used during booking:",
            placeholder="e.g. 9876543210"
        )
    else:
        return _build_welcome(session)


def _handle_name(session, msg):
    if len(msg) < 2:
        return _resp("Please enter a valid full name (at least 2 characters):",
                     placeholder="Your full name")
    _save_session(session, {'state': 'AWAITING_AGE', 'temp_name': msg})
    return _resp(
        f"Nice to meet you, **{msg}**! 😊\n\nWhat is your **age**?",
        placeholder="Enter your age (e.g. 28)"
    )


def _handle_age(session, msg):
    try:
        age = int(msg)
        if age <= 0 or age > 120:
            raise ValueError
    except ValueError:
        return _resp("Please enter a valid age (1–120):", placeholder="Your age")

    _save_session(session, {'state': 'AWAITING_GENDER', 'temp_age': age})
    return _resp(
        "What is your **gender**?",
        buttons=["Male", "Female", "Other"]
    )


def _handle_gender(session, msg):
    g = msg.strip().capitalize()
    if g not in ['Male', 'Female', 'Other']:
        return _resp("Please select your gender:",
                     buttons=["Male", "Female", "Other"])
    _save_session(session, {'state': 'AWAITING_PHONE', 'temp_gender': g})
    return _resp(
        "What is your **phone number**?",
        placeholder="e.g. 9876543210"
    )


def _handle_phone(session, msg):
    import re
    clean = re.sub(r'[\s\-()]+', '', msg)
    if not re.match(r'^\+?[1-9]\d{6,14}$', clean):
        return _resp("Please enter a valid phone number:",
                     placeholder="e.g. 9876543210")
    _save_session(session, {'state': 'AWAITING_EMAIL', 'temp_phone': clean})
    return _resp(
        "What is your **email address**? (Optional — type 'skip' to continue)",
        buttons=["Skip"],
        placeholder="your@email.com or 'skip'"
    )


def _handle_email(session, msg):
    import re
    email = None
    if msg.lower() not in ['skip', 'no', 'none', '-']:
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', msg):
            return _resp("Please enter a valid email or type **Skip**:",
                         buttons=["Skip"], placeholder="your@email.com")
        email = msg.lower()

    _save_session(session, {'state': 'AWAITING_PROBLEM', 'temp_email': email})
    return _resp(
        "Please briefly describe your **symptoms or reason for visit**:",
        placeholder="e.g. Chest pain, fever, skin rash…"
    )


def _handle_problem(session, msg):
    if len(msg) < 3:
        return _resp("Please describe your symptoms in a few words:",
                     placeholder="e.g. Headache, back pain…")
    _save_session(session, {'state': 'AWAITING_DEPT', 'temp_problem': msg})

    dept_buttons = list(slot_service.DEPARTMENTS.keys())
    return _resp(
        "Which **department** would you like to visit?",
        buttons=dept_buttons
    )


def _handle_dept(session, msg):
    # Case-insensitive dept match
    selected = None
    for dept in slot_service.DEPARTMENTS:
        if msg.lower() == dept.lower() or dept.lower() in msg.lower():
            selected = dept
            break

    if not selected:
        return _resp(
            "Please select a department:",
            buttons=list(slot_service.DEPARTMENTS.keys())
        )

    _save_session(session, {'state': 'AWAITING_DOCTOR', 'temp_dept': selected})
    doctors = slot_service.DEPARTMENTS[selected]['doctors']
    return _resp(
        f"Great! Here are the available doctors in **{selected}**:\n\nPlease select your preferred doctor:",
        buttons=doctors
    )


def _handle_doctor(session, msg):
    selected = None
    for doc in slot_service.DOCTORS_LIST:
        if msg.lower() == doc.lower() or doc.lower() in msg.lower():
            selected = doc
            break

    if not selected:
        dept    = session.temp_dept or list(slot_service.DEPARTMENTS.keys())[0]
        doctors = slot_service.DEPARTMENTS.get(dept, {}).get('doctors', slot_service.DOCTORS_LIST)
        return _resp("Please select a valid doctor:", buttons=doctors)

    dates = slot_service.get_available_dates(selected)
    if not dates:
        _save_session(session, {'state': 'MAIN_MENU'})
        return _resp(
            f"Sorry, no slots available for **{selected}** in the next 30 days. Please try another doctor.",
            buttons=["📅 Book Appointment", "👨‍⚕️ Our Doctors"]
        )

    _save_session(session, {'state': 'AWAITING_DATE', 'temp_doctor': selected})
    date_buttons = []
    for d in dates:
        try:
            dt = datetime.datetime.strptime(d, "%Y-%m-%d")
            date_buttons.append(dt.strftime("%d %b %Y") + f"|{d}")
        except ValueError:
            date_buttons.append(d)

    return _resp(
        f"Available dates for **{selected}**:\n\nSelect a date for your appointment:",
        buttons=[d.split("|")[0] if "|" in d else d for d in date_buttons],
        input_type='date',
        placeholder="YYYY-MM-DD"
    )


def _handle_date(session, msg):
    doctor = session.temp_doctor

    # Accept display format "DD Mon YYYY" by reverse-mapping
    date_str = msg.strip()
    if len(date_str) == 10 and '-' in date_str:
        pass  # already YYYY-MM-DD
    else:
        try:
            dt = datetime.datetime.strptime(date_str, "%d %b %Y")
            date_str = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    try:
        y, mo, d = map(int, date_str.split('-'))
        datetime.date(y, mo, d)
    except (ValueError, AttributeError):
        return _resp("Please enter a valid date (YYYY-MM-DD):",
                     input_type='date', placeholder="YYYY-MM-DD")

    slots = slot_service.get_available_slots(doctor, date_str)
    if not slots:
        return _resp(
            f"No available slots for **{doctor}** on {date_str}. Please choose another date:",
            input_type='date', placeholder="YYYY-MM-DD"
        )

    _save_session(session, {'state': 'AWAITING_SLOT', 'temp_date': date_str})

    # Format times nicely for buttons
    def fmt_time(t):
        try:
            return datetime.datetime.strptime(t, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            return t

    slot_buttons = [fmt_time(s) + f"|{s}" for s in slots]
    return _resp(
        f"Available slots for **{doctor}** on {date_str}:",
        buttons=[s.split("|")[0] for s in slot_buttons]
    )


def _handle_slot(session, msg):
    doctor   = session.temp_doctor
    date_str = session.temp_date

    # Parse display format "HH:MM AM/PM"
    time_str = msg.strip()
    if 'AM' in time_str.upper() or 'PM' in time_str.upper():
        try:
            t = datetime.datetime.strptime(time_str.strip(), "%I:%M %p")
            time_str = t.strftime("%H:%M")
        except ValueError:
            pass

    # Normalise short format
    if len(time_str) == 4 and ':' in time_str:
        time_str = "0" + time_str

    slots = slot_service.get_available_slots(doctor, date_str)
    if time_str not in slots:
        def fmt_time(t):
            try:
                return datetime.datetime.strptime(t, "%H:%M").strftime("%I:%M %p")
            except ValueError:
                return t
        return _resp(
            "That slot is unavailable. Please choose from the available times:",
            buttons=[fmt_time(s) for s in slots]
        )

    _save_session(session, {'state': 'AWAITING_CONFIRMATION', 'temp_slot': time_str})

    def fmt(t):
        try:
            return datetime.datetime.strptime(t, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            return t

    summary = (
        f"📋 **Booking Summary**\n\n"
        f"👤 Name: {session.temp_name}\n"
        f"🎂 Age: {session.temp_age}  |  ⚧ Gender: {session.temp_gender}\n"
        f"📞 Phone: {session.temp_phone}\n"
        f"🏥 Department: {session.temp_dept}\n"
        f"👨‍⚕️ Doctor: {doctor}\n"
        f"📅 Date: {date_str}\n"
        f"⏰ Time: {fmt(time_str)}\n"
        f"🩺 Symptoms: {session.temp_problem}\n\n"
        f"Please **confirm** your appointment or **go back** to change details."
    )
    return _resp(summary, buttons=["✅ Confirm Booking", "🔄 Start Over"])


def _handle_confirmation(session, msg):
    if 'confirm' in msg.lower():
        success, result = slot_service.book_appointment_transaction(
            phone_number=session.temp_phone,
            name=session.temp_name,
            age=session.temp_age,
            gender=session.temp_gender,
            problem=session.temp_problem,
            doctor=session.temp_doctor,
            date_str=session.temp_date,
            time_str=session.temp_slot,
            email=session.temp_email,
            department=session.temp_dept,
        )

        # Reset session
        _save_session(session, {
            'state': 'MAIN_MENU',
            'temp_name': None, 'temp_age': None, 'temp_gender': None,
            'temp_problem': None, 'temp_phone': None, 'temp_email': None,
            'temp_dept': None, 'temp_doctor': None, 'temp_date': None,
            'temp_slot': None
        })

        if success:
            # Link chat messages to patient record
            try:
                ChatMessage.query.filter_by(
                    session_id=session.id, patient_id=None
                ).update({'patient_id': result})
                db.session.commit()
            except Exception:
                db.session.rollback()

            # Send confirmation notification
            try:
                from app.services.communication_service import notify_appointment_confirmed
                from app.models.models import Patient
                patient = Patient.query.get(result)
                if patient:
                    notify_appointment_confirmed(patient, channel='web')
            except Exception as e:
                logger.error(f"Confirmation notification error: {e}")

            return _resp(
                ["✅ **Appointment Booked Successfully!**",
                 f"Your appointment ID is **#{result}**. We look forward to seeing you! 🏥",
                 "Is there anything else I can help you with?"],
                buttons=["📅 Book Another Appointment", "🏠 Main Menu"]
            )
        else:
            return _resp(
                [f"❌ Booking failed: {result}",
                 "The slot may have just been taken. Please try again."],
                buttons=["📅 Book Appointment", "🏠 Main Menu"]
            )
    else:
        # Start over
        _save_session(session, {'state': 'WELCOME'})
        return _build_welcome(session)


def _handle_show_doctors(session, msg):
    _save_session(session, {'state': 'MAIN_MENU'})
    lines = ["👨‍⚕️ **Our Medical Team**\n"]
    for dept, info in slot_service.DEPARTMENTS.items():
        lines.append(f"{info['icon']} **{dept}**")
        for doc in info['doctors']:
            lines.append(f"   • {doc}")
    lines.append("\nWould you like to book an appointment?")
    return _multi(lines, buttons=["📅 Book Appointment", "🏠 Main Menu"])


def _handle_show_departments(session, msg):
    _save_session(session, {'state': 'MAIN_MENU'})
    lines = ["🏥 **Our Departments**\n"]
    for dept, info in slot_service.DEPARTMENTS.items():
        lines.append(f"{info['icon']} **{dept}**\n   {info['description']}")
    return _multi(lines, buttons=["📅 Book Appointment", "🏠 Main Menu"])


def _handle_show_info(session, msg):
    from app.config import Config
    _save_session(session, {'state': 'MAIN_MENU'})
    return _resp(
        [
            "📍 **ABC Hospital Information**",
            f"🏥 {Config.HOSPITAL_NAME}\n"
            f"📍 {Config.HOSPITAL_ADDRESS}\n"
            f"📞 {Config.HOSPITAL_PHONE}\n"
            f"✉️ {Config.HOSPITAL_EMAIL}\n"
            f"🕐 {Config.HOSPITAL_HOURS}",
            "🚨 **Emergency**: Dial 112 or visit our Emergency Wing (open 24/7)"
        ],
        buttons=["📅 Book Appointment", "🏠 Main Menu"]
    )


def _handle_cancel_flow(session, msg):
    from app.models.models import Patient
    import re
    clean = re.sub(r'[\s\-()]+', '', msg)

    # Find appointments by phone
    appointments = Patient.query.filter(
        Patient.phone_number.like(f"%{clean[-10:]}%"),
        Patient.booking_status.in_(['Scheduled', 'Confirmed'])
    ).all()

    _save_session(session, {'state': 'MAIN_MENU'})

    if not appointments:
        return _resp(
            "No active appointments found for that number.\n\nPlease contact us at the hospital reception.",
            buttons=["📅 Book Appointment", "🏠 Main Menu"]
        )

    lines = [f"Found **{len(appointments)}** active appointment(s):\n"]
    for appt in appointments:
        try:
            t = datetime.datetime.strptime(appt.booking_time, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            t = appt.booking_time
        lines.append(
            f"• **#{appt.id}** — {appt.doctor} on {appt.booking_date} at {t}"
        )
    lines.append("\nTo cancel, please contact our admin desk or visit the hospital reception.")
    lines.append(f"📞 {__import__('app.config', fromlist=['Config']).Config.HOSPITAL_PHONE}")

    return _multi(lines, buttons=["📅 Book New Appointment", "🏠 Main Menu"])
