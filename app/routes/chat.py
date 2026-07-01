"""
Web Chat API Routes
===================
REST endpoints consumed by the browser chat widget (chat.js).
"""

import logging
import datetime
from flask import Blueprint, request, jsonify
from app.services import web_chat_service, slot_service

logger = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/api/chat', methods=['POST'])
def chat_message():
    """Process a chat message and return bot response."""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json(silent=True) or {}
    session_key  = data.get('session_key', '').strip()
    message_text = data.get('message', '').strip()

    if not session_key:
        return jsonify({'error': 'session_key is required'}), 400
    if not message_text:
        return jsonify({'error': 'message is required'}), 400

    try:
        response = web_chat_service.handle_web_message(session_key, message_text)
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            'messages': ['I encountered an issue. Please try again.'],
            'buttons':  ['🏠 Main Menu'],
            'input':    {'type': 'text', 'placeholder': 'Type your message…'}
        }), 200  # Always 200 so the widget doesn't break


@chat_bp.route('/api/chat/init', methods=['POST'])
def chat_init():
    """Initialise a chat session and return the welcome message."""
    data        = request.get_json(silent=True) or {}
    session_key = data.get('session_key', '').strip()

    if not session_key:
        return jsonify({'error': 'session_key is required'}), 400

    try:
        session  = web_chat_service.get_or_create_session(session_key)
        response = web_chat_service._build_welcome(session)
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Chat init error: {e}")
        return jsonify({
            'messages': ['Welcome to ABC Hospital! 👋 How can I help you?'],
            'buttons':  ['📅 Book Appointment', '🏥 Departments', '📍 Hospital Info'],
            'input':    {'type': 'text', 'placeholder': 'Type your message…'}
        }), 200


@chat_bp.route('/api/slots/<doctor>/<date_str>', methods=['GET'])
def get_slots(doctor, date_str):
    """Returns available time slots for a doctor on a specific date."""
    try:
        slots = slot_service.get_available_slots(doctor, date_str)
        # Format for display
        formatted = []
        for s in slots:
            try:
                display = datetime.datetime.strptime(s, "%H:%M").strftime("%I:%M %p")
            except ValueError:
                display = s
            formatted.append({'value': s, 'display': display})
        return jsonify({'slots': formatted, 'count': len(formatted)}), 200
    except Exception as e:
        logger.error(f"Slots API error: {e}")
        return jsonify({'error': 'Could not fetch slots', 'slots': []}), 500


@chat_bp.route('/api/dates/<doctor>', methods=['GET'])
def get_dates(doctor):
    """Returns next available dates for a doctor."""
    try:
        dates = slot_service.get_available_dates(doctor)
        formatted = []
        for d in dates:
            try:
                display = datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d %b %Y")
            except ValueError:
                display = d
            formatted.append({'value': d, 'display': display})
        return jsonify({'dates': formatted}), 200
    except Exception as e:
        logger.error(f"Dates API error: {e}")
        return jsonify({'error': 'Could not fetch dates', 'dates': []}), 500


@chat_bp.route('/api/departments', methods=['GET'])
def get_departments():
    """Returns department and doctor listing."""
    try:
        data = {}
        for dept, info in slot_service.DEPARTMENTS.items():
            data[dept] = {
                'icon':        info.get('icon', '🏥'),
                'doctors':     info.get('doctors', []),
                'description': info.get('description', '')
            }
        return jsonify({'departments': data}), 200
    except Exception as e:
        logger.error(f"Departments API error: {e}")
        return jsonify({'departments': {}}), 500


@chat_bp.route('/api/calendar/<date_str>', methods=['GET'])
def calendar_data(date_str):
    """Returns appointment and slot summary for a calendar date (admin use)."""
    try:
        from app.services.analytics_service import get_appointments_for_date
        from app.services.slot_service import get_slots_summary

        appointments = get_appointments_for_date(date_str)
        slots_summary = get_slots_summary(date_str)

        appts_data = []
        for a in appointments:
            try:
                t = datetime.datetime.strptime(a.booking_time, "%H:%M").strftime("%I:%M %p")
            except ValueError:
                t = a.booking_time
            appts_data.append({
                'id':       a.id,
                'name':     a.name,
                'doctor':   a.doctor,
                'dept':     a.department or '',
                'time':     t,
                'time_raw': a.booking_time,
                'status':   a.booking_status,
                'phone':    a.phone_number,
            })

        return jsonify({
            'date':         date_str,
            'appointments': appts_data,
            'slots':        slots_summary,
            'total':        len(appts_data),
        }), 200
    except Exception as e:
        logger.error(f"Calendar API error: {e}")
        return jsonify({'error': str(e)}), 500
