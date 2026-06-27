# 🏥 Hospital Appointment Booking System & WhatsApp Chatbot

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Flask Framework](https://img.shields.io/badge/framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Database ORM](https://img.shields.io/badge/orm-SQLAlchemy-red.svg)](https://www.sqlalchemy.org/)
[![Webhook Integration](https://img.shields.io/badge/integration-Meta%20WhatsApp%20Cloud-green.svg)](https://developers.facebook.com/)

A production-ready, clean-architecture Hospital Appointment Booking System MVP featuring an automated WhatsApp chatbot integration. Patients can view real-time slot availability, input consultation details, and complete dynamic bookings directly via WhatsApp.

---

## 🏗️ Architecture & Folder Structure

This application follows clean-architecture guidelines:

```text
├── app/
│   ├── database/       # SQLAlchemy engine database connection bindings
│   ├── models/         # SQLAlchemy Schemas for Patients, AvailableSlots, BotStates
│   ├── routes/         # Web views and Webhook API controllers
│   ├── services/       # Core state machine bot flow & transactional slot mechanics
│   ├── static/         # Public CSS styles & assets
│   ├── templates/      # Jinja2 HTML layout views
│   ├── config.py       # Modular environment variable reader
│   └── __init__.py     # Flask factory app setup with custom stdout/stderr loggers
├── app.py              # Root launcher entrypoint script
├── requirements.txt    # Production dependencies
├── runtime.txt         # Targeted platform runtime version
├── render.yaml         # Blueprint specification for Render
├── Procfile            # Gunicorn startup instruction file
├── EXTERNAL_SETUP.md   # Step-by-step Meta WhatsApp Cloud API configuration guide
└── .env.example        # Environment variable configuration template
```

---

## 🛠️ Tech Stack
- **Backend Framework**: Python (Flask)
- **Database ORM**: SQLAlchemy (supporting PostgreSQL in production and SQLite fallback locally)
- **WSGI Production Server**: Gunicorn
- **Styling Layout**: Vanilla CSS with modern typography & sleek interactive transitions.

---

## 🚀 Setup & Installation

### 1. Local Application Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "whatsapp bot"
   ```

2. **Create and activate a python virtual environment**:
   - On Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Environment Variables**:
   Copy `.env.example` to `.env` and fill in the values:
   ```bash
   copy .env.example .env
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

---

## 💬 WhatsApp Integration & Local Webhook Testing

To connect this application with the WhatsApp Business API and test incoming messages locally:
1. Setup a **Meta Developer App** and WhatsApp Platform.
2. Run **Ngrok** to create a public HTTPS tunnel.
3. Configure the **Webhook Callback URL** on the Meta Portal.

👉 **Follow our detailed step-by-step instructions in the [External Setup Guide](EXTERNAL_SETUP.md)**.

---

## 🌐 Deploying to Render with PostgreSQL

This repository is pre-configured for one-click Render Blueprint Deployments:

1. Push this project repository to GitHub.
2. In your Render Dashboard, click **New** ➔ **Blueprint**.
3. Link your GitHub repository.
4. Render automatically parses `render.yaml` to spin up:
   - A **PostgreSQL Web Database** service.
   - A **Python Flask Web Service** running under Gunicorn.
5. In your Web Service settings on Render, populate the required environment variables:
   - `WHATSAPP_TOKEN`
   - `WHATSAPP_PHONE_NUMBER_ID`
   - `WHATSAPP_VERIFY_TOKEN`
