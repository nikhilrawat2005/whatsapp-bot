# Hospital Appointment Booking System & WhatsApp Chatbot

A production-ready, clean-architecture Hospital Appointment Booking System MVP featuring an automated WhatsApp chatbot integration. It enables patients to view real-time slot availability, input consultation details, and complete dynamic bookings.

---

## Architecture & Folder Structure

We follow a clean, modular pythonic project structure:

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
└── .env.example        # Environment variable configuration template
```

---

## Tech Stack
- **Backend Framework**: Python (Flask)
- **Database ORM**: SQLAlchemy (supporting PostgreSQL in production and SQLite fallback locally)
- **WSGI Production Server**: Gunicorn
- **Styling Layout**: Vanilla CSS with modern typography & sleek interactive transitions.

---

## Environment Variables Configuration

Create a `.env` file in the root project folder containing:
```env
PORT=5000
SECRET_KEY=production-session-secret-key-string-here
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
WHATSAPP_TOKEN=your_meta_permanent_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id_here
WHATSAPP_VERIFY_TOKEN=abc_hospital_verify_token_123
```

---

## Local Installation

1. Clone the repository and navigate inside the project folder:
   ```bash
   git clone <repository-url>
   cd "whatsapp bot"
   ```
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install the dependencies:
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

## Deploying to Render with PostgreSQL

This repository is pre-configured for one-click Blueprint Deployments.

1. Push this project repository to GitHub.
2. In your Render Dashboard, click **New** ➔ **Blueprint**.
3. Link your GitHub repository.
4. Render automatically parses `render.yaml` to spin up:
   - A **PostgreSQL Web Database** service.
   - A **Python Flask Web Service** running under Gunicorn.
5. In your Web Service settings, populate `WHATSAPP_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID`.

---

## Meta WhatsApp webhook integration

1. Obtain your access credentials from the [Meta Developers Console](https://developers.facebook.com/).
2. Run a public URL tunnel locally using ngrok:
   ```bash
   ngrok http 5000
   ```
3. Set your Meta webhook callback to `https://<your-ngrok-or-render-domain>/webhook` and verify token with `abc_hospital_verify_token_123`.
4. Subscribe to the **messages** webhook field on the WhatsApp API configuration panel.
