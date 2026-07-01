"""
Analytics Service
=================
Provides all data for the admin dashboard, charts, and statistics.
All queries are centralised here — routes stay thin.
"""

import datetime
import logging
from collections import defaultdict
from app.database.db import db
from app.models.models import Patient, AvailableSlot

logger = logging.getLogger(__name__)


def get_dashboard_stats():
    """Returns key metric counts for the top stats cards."""
    today = datetime.date.today().strftime("%Y-%m-%d")

    total_patients   = Patient.query.count()
    today_appts      = Patient.query.filter_by(booking_date=today).count()
    pending          = Patient.query.filter_by(booking_status='Scheduled').count()
    confirmed        = Patient.query.filter_by(booking_status='Confirmed').count()
    completed        = Patient.query.filter_by(booking_status='Completed').count()
    cancelled        = Patient.query.filter_by(booking_status='Cancelled').count()
    available_slots  = AvailableSlot.query.filter(
        AvailableSlot.date >= today,
        AvailableSlot.is_booked == 0
    ).count()

    # Upcoming (future scheduled/confirmed)
    upcoming = Patient.query.filter(
        Patient.booking_date > today,
        Patient.booking_status.in_(['Scheduled', 'Confirmed'])
    ).count()

    return {
        'total_patients':  total_patients,
        'today_appts':     today_appts,
        'upcoming':        upcoming,
        'pending':         pending,
        'confirmed':       confirmed,
        'completed':       completed,
        'cancelled':       cancelled,
        'available_slots': available_slots,
    }


def get_today_schedule():
    """Returns today's appointments ordered by booking time."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    appointments = Patient.query.filter_by(booking_date=today)\
        .order_by(Patient.booking_time.asc()).all()
    return appointments


def get_appointments_for_date(date_str):
    """Returns appointments for a specific date, ordered by time."""
    return Patient.query.filter_by(booking_date=date_str)\
        .order_by(Patient.booking_time.asc()).all()


def get_weekly_appointments():
    """Returns appointments for the current week (Mon–Sun)."""
    today     = datetime.date.today()
    monday    = today - datetime.timedelta(days=today.weekday())
    sunday    = monday + datetime.timedelta(days=6)
    mon_str   = monday.strftime("%Y-%m-%d")
    sun_str   = sunday.strftime("%Y-%m-%d")

    return Patient.query.filter(
        Patient.booking_date >= mon_str,
        Patient.booking_date <= sun_str
    ).order_by(Patient.booking_date.asc(), Patient.booking_time.asc()).all()


def get_weekly_stats():
    """Returns day-by-day appointment counts for the current week (for line chart)."""
    today  = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    labels = []
    counts = []

    for i in range(7):
        day     = monday + datetime.timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        count   = Patient.query.filter(
            Patient.booking_date == day_str,
            Patient.booking_status != 'Cancelled'
        ).count()
        labels.append(day.strftime("%a"))
        counts.append(count)

    return {'labels': labels, 'counts': counts}


def get_peak_hours():
    """Returns appointment counts per hour slot (for bar chart)."""
    all_appts = Patient.query.filter(
        Patient.booking_status != 'Cancelled'
    ).all()

    hour_counts = defaultdict(int)
    for appt in all_appts:
        if appt.booking_time:
            try:
                hour = int(appt.booking_time.split(':')[0])
                hour_counts[hour] += 1
            except (ValueError, IndexError):
                pass

    labels = []
    counts = []
    for hour in range(9, 18):
        if hour == 13:
            continue  # Lunch break
        label = datetime.time(hour, 0).strftime("%I:%M %p")
        labels.append(label)
        counts.append(hour_counts.get(hour, 0))

    return {'labels': labels, 'counts': counts}


def get_department_distribution():
    """Returns appointment counts per department (for donut chart)."""
    all_appts = Patient.query.filter(
        Patient.booking_status != 'Cancelled'
    ).all()

    dept_counts = defaultdict(int)
    for appt in all_appts:
        dept = appt.department or 'Unknown'
        dept_counts[dept] += 1

    return {
        'labels': list(dept_counts.keys()),
        'counts': list(dept_counts.values())
    }


def get_gender_distribution():
    """Returns gender breakdown (for pie chart)."""
    all_appts = Patient.query.filter(
        Patient.booking_status != 'Cancelled'
    ).all()
    gender_counts = defaultdict(int)
    for appt in all_appts:
        gender_counts[appt.gender or 'Unknown'] += 1

    return {
        'labels': list(gender_counts.keys()),
        'counts': list(gender_counts.values())
    }


def get_status_distribution():
    """Returns counts per status (for the status donut)."""
    statuses = ['Scheduled', 'Confirmed', 'Completed', 'Cancelled']
    counts   = [Patient.query.filter_by(booking_status=s).count() for s in statuses]
    return {'labels': statuses, 'counts': counts}


def get_busiest_doctor():
    """Returns the doctor with the most non-cancelled appointments."""
    from sqlalchemy import func
    result = db.session.query(
        Patient.doctor,
        func.count(Patient.id).label('total')
    ).filter(
        Patient.booking_status != 'Cancelled'
    ).group_by(Patient.doctor).order_by(func.count(Patient.id).desc()).first()

    if result:
        return {'name': result.doctor, 'count': result.total}
    return {'name': 'N/A', 'count': 0}


def get_doctor_stats():
    """Returns per-doctor appointment stats."""
    from sqlalchemy import func
    from app.services.slot_service import DOCTORS_LIST

    results = db.session.query(
        Patient.doctor,
        func.count(Patient.id).label('total'),
        func.sum(db.case((Patient.booking_status == 'Completed', 1), else_=0)).label('completed'),
        func.sum(db.case((Patient.booking_status == 'Cancelled', 1), else_=0)).label('cancelled'),
        func.sum(db.case((Patient.booking_status.in_(['Scheduled', 'Confirmed']), 1), else_=0)).label('pending'),
    ).group_by(Patient.doctor).all()

    stats = {r.doctor: {
        'total':     r.total,
        'completed': r.completed or 0,
        'cancelled': r.cancelled or 0,
        'pending':   r.pending or 0,
    } for r in results}

    # Ensure all doctors are present
    for doc in DOCTORS_LIST:
        if doc not in stats:
            stats[doc] = {'total': 0, 'completed': 0, 'cancelled': 0, 'pending': 0}

    return stats
