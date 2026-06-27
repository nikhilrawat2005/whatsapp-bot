import logging
from flask import Blueprint, request, render_template, redirect, url_for
from app.database.db import db
from app.models.models import Patient
from app.config import Config
from app.services import slot_service

logger = logging.getLogger(__name__)
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def home():
    """Renders the hospital landing page."""
    return render_template('index.html', wa_number_id=Config.WHATSAPP_PHONE_NUMBER_ID)

@web_bp.route('/admin')
def admin_dashboard():
    """Renders the Admin Dashboard with filters and search functionality."""
    # Extract filter inputs
    search = request.args.get('search', '').strip()
    doctor = request.args.get('doctor', '').strip()
    date = request.args.get('date', '').strip()
    status = request.args.get('status', '').strip()
    
    # Build query dynamically using SQLAlchemy
    query = Patient.query
    
    if search:
        query = query.filter(
            (Patient.name.like(f"%{search}%")) | 
            (Patient.phone_number.like(f"%{search}%"))
        )
        
    if doctor:
        query = query.filter_by(doctor=doctor)
        
    if date:
        query = query.filter_by(booking_date=date)
        
    if status:
        query = query.filter_by(booking_status=status)
        
    appointments = query.order_by(Patient.booking_date.desc(), Patient.booking_time.desc()).all()
    
    return render_template(
        'admin.html',
        appointments=appointments,
        doctors=slot_service.DOCTORS_LIST,
        filters={'search': search, 'doctor': doctor, 'date': date, 'status': status}
    )

@web_bp.route('/admin/complete/<int:appt_id>', methods=['POST'])
def complete_appointment(appt_id):
    """Marks an appointment as Completed."""
    try:
        patient = Patient.query.get(appt_id)
        if patient:
            patient.booking_status = 'Completed'
            db.session.commit()
            logger.info(f"Marked appointment ID {appt_id} as completed.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error completing appointment {appt_id}: {e}")
        
    return redirect(url_for('web.admin_dashboard'))

@web_bp.route('/admin/cancel/<int:appt_id>', methods=['POST'])
def cancel_appointment(appt_id):
    """Cancels appointment and frees up slot dynamically via slot manager."""
    success = slot_service.release_appointment_slot(appt_id)
    if not success:
        logger.error(f"Failed to cancel appointment {appt_id} properly.")
    return redirect(url_for('web.admin_dashboard'))
