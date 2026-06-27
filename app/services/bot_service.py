import datetime
import logging
import requests
from app.config import Config
from app.database.db import db
from app.models.models import BotState
from app.services import slot_service

logger = logging.getLogger(__name__)

def send_whatsapp_message(to, body):
    """Sends a text message using Meta WhatsApp Cloud API."""
    if not Config.WHATSAPP_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
        # Mock/Log for local debugging when keys are not configured
        logger.info(f"[MOCK WHATSAPP OUTGOING to {to}]: {body}")
        return True
        
    url = f"https://graph.facebook.com/v18.0/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "body": body
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logger.error(f"Meta API responded with status {response.status_code}: {response.text}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error calling Meta WhatsApp API: {e}")
        return False

def get_or_create_state(phone_number):
    """Retrieves or creates a bot state record for a given phone number."""
    state_rec = BotState.query.filter_by(phone_number=phone_number).first()
    if not state_rec:
        state_rec = BotState(phone_number=phone_number, state='WELCOME')
        db.session.add(state_rec)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating state record: {e}")
            # Try to fetch again in case of race condition
            state_rec = BotState.query.filter_by(phone_number=phone_number).first()
    return state_rec

def update_state(phone_number, updates):
    """Updates bot state key-value attributes dynamically."""
    try:
        state_rec = BotState.query.filter_by(phone_number=phone_number).first()
        if state_rec:
            for k, v in updates.items():
                setattr(state_rec, k, v)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating session state for {phone_number}: {e}")

def handle_incoming_message(phone_number, message_text):
    """Processes incoming chatbot state interactions step-by-step."""
    msg = message_text.strip()
    session = get_or_create_state(phone_number)
    state = session.state
    
    # 1. Start Flow
    if msg.lower() in ['hi', 'hello', 'hey', 'start', 'book']:
        update_state(phone_number, {'state': 'AWAITING_NAME'})
        send_whatsapp_message(phone_number, "Welcome 👋 to ABC Hospital Booking Bot.\n\nPlease enter your Full Name:")
        return
        
    if state == 'WELCOME':
        update_state(phone_number, {'state': 'AWAITING_NAME'})
        send_whatsapp_message(phone_number, "Welcome 👋 to ABC Hospital Booking Bot.\n\nPlease enter your Full Name:")
        return

    # 2. Awaiting Name
    elif state == 'AWAITING_NAME':
        if len(msg) < 2:
            send_whatsapp_message(phone_number, "Please enter a valid name (at least 2 letters):")
            return
        update_state(phone_number, {
            'state': 'AWAITING_AGE',
            'temp_name': msg
        })
        send_whatsapp_message(phone_number, f"Thank you, {msg}. Now, please enter your age (numbers only):")
        return

    # 3. Awaiting Age
    elif state == 'AWAITING_AGE':
        try:
            age = int(msg)
            if age <= 0 or age > 120:
                raise ValueError
        except ValueError:
            send_whatsapp_message(phone_number, "Please enter a valid age (e.g., 25):")
            return
            
        update_state(phone_number, {
            'state': 'AWAITING_GENDER',
            'temp_age': age
        })
        send_whatsapp_message(phone_number, "What is your gender?\n\nRespond with one of the following:\n- Male\n- Female\n- Other")
        return

    # 4. Awaiting Gender
    elif state == 'AWAITING_GENDER':
        gender_input = msg.strip().capitalize()
        if gender_input not in ['Male', 'Female', 'Other']:
            send_whatsapp_message(phone_number, "Invalid input. Please respond with:\n- Male\n- Female\n- Other")
            return
            
        update_state(phone_number, {
            'state': 'AWAITING_PROBLEM',
            'temp_gender': gender_input
        })
        send_whatsapp_message(phone_number, "What problem or symptoms are you facing? (Provide a short description):")
        return

    # 5. Awaiting Problem
    elif state == 'AWAITING_PROBLEM':
        if len(msg) < 3:
            send_whatsapp_message(phone_number, "Please describe the problem in a few words:")
            return
            
        update_state(phone_number, {
            'state': 'AWAITING_DOCTOR',
            'temp_problem': msg
        })
        
        # Show list of doctors
        doctors_msg = "Which doctor would you like to consult?\n\nSelect by typing the exact name:\n"
        for doc in slot_service.DOCTORS_LIST:
            doctors_msg += f"- {doc}\n"
        send_whatsapp_message(phone_number, doctors_msg)
        return

    # 6. Awaiting Doctor Selection
    elif state == 'AWAITING_DOCTOR':
        # Match case insensitively but store standardized version
        selected_doctor = None
        for doc in slot_service.DOCTORS_LIST:
            if msg.lower() == doc.lower():
                selected_doctor = doc
                break
                
        if not selected_doctor:
            doctors_msg = "Invalid doctor selection. Please choose from the list:\n"
            for doc in slot_service.DOCTORS_LIST:
                doctors_msg += f"- {doc}\n"
            send_whatsapp_message(phone_number, doctors_msg)
            return
            
        # Get future available dates
        dates = slot_service.get_available_dates(selected_doctor)
        if not dates:
            send_whatsapp_message(phone_number, f"Sorry, there are no slots available for {selected_doctor} in the next 30 days.")
            update_state(phone_number, {'state': 'WELCOME'})
            return
            
        update_state(phone_number, {
            'state': 'AWAITING_DATE',
            'temp_doctor': selected_doctor
        })
        
        dates_msg = f"Available dates for {selected_doctor}:\n\n"
        for d in dates:
            dates_msg += f"- {d}\n"
        dates_msg += "\nPlease type the date you want to book (YYYY-MM-DD):"
        send_whatsapp_message(phone_number, dates_msg)
        return

    # 7. Awaiting Date Selection
    elif state == 'AWAITING_DATE':
        doctor = session.temp_doctor
        try:
            year, month, day = map(int, msg.split('-'))
            datetime.date(year, month, day)
        except ValueError:
            send_whatsapp_message(phone_number, "Please enter date in correct format (YYYY-MM-DD):")
            return
            
        slots = slot_service.get_available_slots(doctor, msg)
        if not slots:
            send_whatsapp_message(phone_number, f"No slots available for {doctor} on {msg}. Please enter another date (YYYY-MM-DD):")
            return
            
        update_state(phone_number, {
            'state': 'AWAITING_SLOT',
            'temp_date': msg
        })
        
        slots_msg = f"Available slots for {doctor} on {msg}:\n\n"
        for s in slots:
            slots_msg += f"- {s}\n"
        slots_msg += "\nPlease type the time you want to book (e.g., 09:30 or 14:00):"
        send_whatsapp_message(phone_number, slots_msg)
        return

    # 8. Awaiting Slot Selection
    elif state == 'AWAITING_SLOT':
        doctor = session.temp_doctor
        date_str = session.temp_date
        
        # Verify valid time slot formats
        time_input = msg.strip()
        if len(time_input) == 4 and ':' in time_input:
            time_input = "0" + time_input
            
        slots = slot_service.get_available_slots(doctor, date_str)
        if time_input not in slots:
            send_whatsapp_message(phone_number, f"Invalid or unavailable slot. Please choose one from below:\n" + "\n".join([f"- {s}" for s in slots]))
            return
            
        update_state(phone_number, {
            'state': 'AWAITING_CONFIRMATION',
            'temp_slot': time_input
        })
        
        confirm_msg = (
            f"Please confirm your booking details:\n\n"
            f"👤 Name: {session.temp_name}\n"
            f"📅 Age: {session.temp_age}\n"
            f"⚧ Gender: {session.temp_gender}\n"
            f"🩺 Symptom: {session.temp_problem}\n"
            f"👨‍⚕️ Doctor: {doctor}\n"
            f"📆 Date: {date_str}\n"
            f"⏰ Time: {time_input}\n\n"
            f"Reply with 'Confirm' to finalize your booking, or 'Restart' to start over."
        )
        send_whatsapp_message(phone_number, confirm_msg)
        return

    # 9. Awaiting Final Confirmation
    elif state == 'AWAITING_CONFIRMATION':
        if msg.lower() == 'confirm':
            success, message = slot_service.book_appointment_transaction(
                phone_number=phone_number,
                name=session.temp_name,
                age=session.temp_age,
                gender=session.temp_gender,
                problem=session.temp_problem,
                doctor=session.temp_doctor,
                date_str=session.temp_date,
                time_str=session.temp_slot
            )
            
            if success:
                send_whatsapp_message(phone_number, "Appointment Booked ✅\n\nThank you for choosing ABC Hospital! We will see you then.")
            else:
                send_whatsapp_message(phone_number, f"Booking Failed ❌\n{message}\n\nPlease type 'Restart' to try booking a different slot.")
                
            update_state(phone_number, {
                'state': 'WELCOME',
                'temp_name': None,
                'temp_age': None,
                'temp_gender': None,
                'temp_problem': None,
                'temp_doctor': None,
                'temp_date': None,
                'temp_slot': None
            })
        elif msg.lower() == 'restart':
            update_state(phone_number, {
                'state': 'WELCOME',
                'temp_name': None,
                'temp_age': None,
                'temp_gender': None,
                'temp_problem': None,
                'temp_doctor': None,
                'temp_date': None,
                'temp_slot': None
            })
            send_whatsapp_message(phone_number, "Let's restart booking process. Reply 'Hello' to begin.")
        else:
            send_whatsapp_message(phone_number, "Please reply 'Confirm' to book your appointment, or 'Restart' to cancel.")
        return
