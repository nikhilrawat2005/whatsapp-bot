# 🏥 AI Digital Hospital Receptionist & Booking System

A production-ready, clean-architecture Hospital Appointment Booking System. It features an automated AI chatbot receptionist on the website, allowing patients to view real-time slot availability, describe symptoms, and book appointments step-by-step. It also includes a fully-featured, modern SaaS Admin Dashboard to manage schedules, patients, settings, and view real-time analytics.

---

## 🏗️ Architecture & Folder Structure

This application uses a modular, layered layout:

```text
├── app/
│   ├── database/       # SQLAlchemy engine database connection bindings
│   │   └── db.py
│   ├── models/         # SQLAlchemy Schemas for Patients, Sessions, Messages, and Settings
│   │   └── models.py
│   ├── routes/         # Web views and Chat REST API controllers
│   │   ├── web.py
│   │   └── chat.py
│   ├── services/       # Core state machine bot flow & transactional slot mechanics
│   │   ├── web_chat_service.py
│   │   ├── slot_service.py
│   │   ├── analytics_service.py
│   │   └── communication_service.py
│   ├── static/         # Public CSS styles & Javascript files
│   │   ├── style.css
│   │   ├── chat.js
│   │   └── admin.js
│   ├── templates/      # Jinja2 HTML layout views
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── admin.html
│   │   ├── analytics.html
│   │   ├── settings.html
│   │   ├── patients.html
│   │   ├── patient_profile.html
│   │   └── appointment_detail.html
│   ├── utils/          # General helper functions and validation utilities
│   │   └── helpers.py
│   ├── config.py       # Modular environment variable reader
│   ├── extensions.py   # Flask extension instances
│   └── __init__.py     # Flask factory app setup with custom stdout/stderr loggers
├── app.py              # Root launcher entrypoint script
├── requirements.txt    # Production dependencies (pinned)
├── runtime.txt         # Targeted platform runtime version
├── Procfile            # Gunicorn startup instruction file
├── RAILWAY_DEPLOYMENT.md # Deployment Guide for Railway
└── .env.example        # Environment variable configuration template
```

---

## 🛠️ Technology Stack
* **Backend Framework**: Python (Flask)
* **Database ORM**: SQLAlchemy (supporting PostgreSQL in production and SQLite fallback locally)
* **WSGI Production Server**: Gunicorn
* **Frontend**: HTML5, Vanilla CSS, Vanilla JS, Chart.js

---

## 🚀 Installation & Local Development

### 1. Prerequisites
Ensure you have Python 3.11+ installed.

### 2. Local Setup
1. Clone the repository and navigate inside the project folder:
   ```bash
   git clone <repository-url>
   cd "whatsapp bot"
   ```
2. Create and activate a python virtual environment:
   - **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install the pinned dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables example:
   ```bash
   copy .env.example .env
   ```
5. Run the application:
   ```bash
   python app.py
   ```

---

## ⚙️ Environment Variables
Below is the basic structure of the `.env` file:
```env
PORT=5000
FLASK_ENV=development
SECRET_KEY=production-session-secret-key-string-here
SESSION_SECRET=production-additional-session-secret-string-here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

---

## 🖥️ Database Configurations
The application supports multi-engine fallbacks:
* **SQLite (Local Dev)**: Used automatically if `DATABASE_URL` is not set. Database file is stored at `instance/hospital.db`.
* **PostgreSQL (Production)**: Used if `DATABASE_URL` is set.

---

## 🌐 Production Deployment (Railway)
This project is fully ready for deployment on **Railway**. 
Please refer to the comprehensive [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) file at the root of the project for setup details and environment configuration instructions.
