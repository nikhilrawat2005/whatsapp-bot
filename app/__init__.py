import os
import sys
import logging
from flask import Flask
from app.config import Config
from app.database.db import db


def setup_logging(app_config):
    """Configures structured logs splitting stdout stream logs by severity level."""
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(app_config.LOG_LEVEL)
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)


def _run_sqlite_migrations(app):
    """Gracefully add new columns to existing SQLite tables without losing data."""
    import sqlite3

    db_path = os.path.join(app.instance_path, 'hospital.db')
    if not os.path.exists(db_path):
        return  # Fresh DB — create_all() handles it

    try:
        conn   = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get existing columns in patients table
        cursor.execute("PRAGMA table_info(patients)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        migrations = [
            ("email",      "ALTER TABLE patients ADD COLUMN email TEXT"),
            ("department", "ALTER TABLE patients ADD COLUMN department TEXT"),
            ("notes",      "ALTER TABLE patients ADD COLUMN notes TEXT"),
        ]
        for col_name, sql in migrations:
            if col_name not in existing_cols:
                cursor.execute(sql)
                logging.getLogger(__name__).info(
                    f"Migration: added column '{col_name}' to patients table."
                )

        conn.commit()
        conn.close()
    except Exception as e:
        logging.getLogger(__name__).warning(f"SQLite migration skipped: {e}")


def create_app():
    """Application factory — initialises logger, database, and registers blueprints."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    setup_logging(Config)

    db.init_app(app)

    # Register blueprints
    from app.routes.web     import web_bp
    from app.routes.chat    import chat_bp   # NEW

    app.register_blueprint(web_bp)
    app.register_blueprint(chat_bp)          # NEW

    with app.app_context():
        # Run SQLite column migrations BEFORE create_all
        _run_sqlite_migrations(app)

        # Create all tables (new tables are added; existing ones untouched)
        db.create_all()

        # Populate slots for next 30 days
        from app.services import slot_service
        slot_service.generate_slots_for_next_30_days()

    return app
