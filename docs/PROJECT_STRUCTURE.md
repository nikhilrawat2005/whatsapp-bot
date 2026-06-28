# 📁 Project Directory Structure

This document details the modular layout and file organization of the Hospital Appointment Booking WhatsApp Bot application.

---

## 1. Directory Tree
```text
├── app/
│   ├── database/       # SQLAlchemy engine database connection bindings
│   │   └── db.py       # Exposes db database connector object
│   ├── models/         # SQLAlchemy Schemas for Patients, AvailableSlots, BotStates
│   │   └── models.py   # Model declarations
│   ├── routes/         # Web views and Webhook API controllers
│   │   ├── web.py      # Main router serving landing page & admin dashboard
│   │   └── webhook.py  # Handler for webhook validation & incoming WhatsApp messages
│   ├── services/       # Core state machine bot flow & transactional slot mechanics
│   │   ├── bot_service.py   # Outgoing API dispatcher & state management engine
│   │   └── slot_service.py  # Slot generator & transactional booker logic
│   ├── static/         # Public CSS styles & assets
│   │   └── style.css   # Theme styles and design configurations
│   ├── templates/      # Jinja2 HTML layout views
│   │   ├── admin.html  # Backend slot & customer filter overview dashboard
│   │   └── index.html  # Clean responsive frontend presentation homepage
│   ├── utils/          # General helper functions and utilities
│   │   ├── __init__.py
│   │   └── helpers.py  # Phone, age, and date validation helpers
│   ├── config.py       # Configuration environment parser
│   ├── extensions.py   # Holds Flask extension instances (SQLAlchemy db)
│   └── __init__.py     # Flask factory app setup with logging configurations
├── docs/               # Detailed documentation files
├── app.py              # Root launcher entrypoint script
├── requirements.txt    # Production dependencies
├── runtime.txt         # Targeted platform runtime version
├── render.yaml         # Blueprint specification for Render
├── Procfile            # Gunicorn startup instruction file
└── .env.example        # Environment variable configuration template
```

---

## 2. File Responsibilities

### 2.1 Core Application
* **`app.py`**: The main entrypoint that initializes the Flask application using the application factory and starts the server.
* **`app/config.py`**: Reads configuration variables from environment variables and sets up default fallback configuration variables.
* **`app/extensions.py`**: Initializes SQLAlchemy extensions to prevent circular import issues in modern project structures.
* **`app/__init__.py`**: Contains the application factory `create_app` function, sets up logging configurations, registers blueprints, and pre-generates appointment slots.

### 2.2 Routes and Controllers
* **`app/routes/web.py`**: Serves the user-facing web pages:
  * `/` (Home): Landing page with description and booking call-to-actions.
  * `/admin` (Admin Panel): Filter, complete, or cancel appointments.
* **`app/routes/webhook.py`**: Webhook endpoint (`/webhook`) that handles Meta validation queries and incoming user messages.

### 2.3 Services
* **`app/services/bot_service.py`**: Orchestrates the WhatsApp conversational workflow (State Machine). It processes inputs step-by-step and maps them to states (`AWAITING_NAME`, `AWAITING_AGE`, etc.).
* **`app/services/slot_service.py`**: Pre-populates daily doctor slots and handles booking/cancellation transactions with SQLAlchemy concurrency locks.

### 2.4 Utils
* **`app/utils/helpers.py`**: Modular helper functions for data validations (phone numbers, ages, dates).
