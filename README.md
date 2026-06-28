# 🏥 Hospital Appointment Booking System & WhatsApp Chatbot

A production-ready, clean-architecture Hospital Appointment Booking System MVP featuring an automated WhatsApp chatbot integration. It enables patients to view real-time slot availability, input consultation details, and complete dynamic bookings.

---

## 📸 Screenshots Placeholder
*Landing page, Web Booking Overview, and WhatsApp interface screenshots can be added here.*

---

## 🏗️ Architecture & Folder Structure

This application uses a modular, layered layout:

```text
├── app/
│   ├── database/       # SQLAlchemy engine database connection bindings
│   │   └── db.py
│   ├── models/         # SQLAlchemy Schemas for Patients, AvailableSlots, BotStates
│   │   └── models.py
│   ├── routes/         # Web views and Webhook API controllers
│   │   ├── web.py
│   │   └── webhook.py
│   ├── services/       # Core state machine bot flow & transactional slot mechanics
│   │   ├── bot_service.py
│   │   └── slot_service.py
│   ├── static/         # Public CSS styles & assets
│   │   └── style.css
│   ├── templates/      # Jinja2 HTML layout views
│   │   ├── admin.html
│   │   └── index.html
│   ├── utils/          # General helper functions and validation utilities
│   │   └── helpers.py
│   ├── config.py       # Modular environment variable reader
│   ├── extensions.py   # Flask extension instances
│   └── __init__.py     # Flask factory app setup with custom stdout/stderr loggers
├── docs/               # Detailed documentation files
│   ├── API.md
│   ├── DATABASE.md
│   ├── DEPLOYMENT.md
│   ├── ENVIRONMENT.md
│   ├── META_SETUP.md
│   ├── PROJECT_STRUCTURE.md
│   └── WEBHOOK_SETUP.md
├── app.py              # Root launcher entrypoint script
├── requirements.txt    # Production dependencies (pinned)
├── runtime.txt         # Targeted platform runtime version
├── render.yaml         # Blueprint specification for Render
├── Procfile            # Gunicorn startup instruction file
└── .env.example        # Environment variable configuration template
```

---

## 🛠️ Technology Stack
* **Backend Framework**: Python (Flask)
* **Database ORM**: SQLAlchemy (supporting PostgreSQL in production and SQLite fallback locally)
* **WSGI Production Server**: Gunicorn
* **Deployment Platform**: Render
* **WhatsApp API Integration**: Meta Cloud API

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
Check out [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) for full descriptions of all variables. Below is the basic structure:
```env
PORT=5000
FLASK_ENV=development
SECRET_KEY=production-session-secret-key-string-here
SESSION_SECRET=production-additional-session-secret-string-here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
WHATSAPP_TOKEN=your_meta_access_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=abc_hospital_verify_token_123
```

---

## 🖥️ Database Configurations
The application supports multi-engine fallbacks:
* **SQLite (Local Dev)**: Used automatically if `DATABASE_URL` is not set. Database file is stored at `instance/hospital.db`.
* **PostgreSQL (Production)**: Used if `DATABASE_URL` is set.
* See [docs/DATABASE.md](docs/DATABASE.md) for detailed schema info.

---

## 🌐 Production Deployment (Render)
This project is configured for **Render Blueprint** deployments:
1. Push your repository to GitHub.
2. In your Render Dashboard, click **New** ➔ **Blueprint**.
3. Connect your GitHub repository.
4. Input the environment variable keys requested.
5. Render will launch your services. Detailed steps are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## 💬 Meta WhatsApp & Webhook Configuration
Learn how to configure the Meta developer account and your webhook endpoints:
* **Meta Setup Guide**: [docs/META_SETUP.md](docs/META_SETUP.md)
* **Webhook Setup Guide**: [docs/WEBHOOK_SETUP.md](docs/WEBHOOK_SETUP.md)
* **API Details**: [docs/API.md](docs/API.md)

---

## 🛑 Troubleshooting & Common Errors

### 1. `psycopg2` Import / Install Errors
Ensure you use `psycopg2-binary` instead of `psycopg2` (pre-configured in `requirements.txt`).

### 2. Webhook verification failing
* Ensure the `WHATSAPP_VERIFY_TOKEN` matches on both your Meta panel and your `.env` file.
* Make sure your server is running and reachable at the provided Ngrok or public URL.

### 3. Messages not sending
* Make sure you are using a verified test recipient phone number in development.
* Check that your `WHATSAPP_TOKEN` has not expired (generate a permanent token to prevent this).

---

## 🔮 Future Improvements
* Add multi-language support to the bot.
* Integrate automated WhatsApp template triggers for booking reminders.
* Enhance admin dashboard authentication and security.

---

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

---

## 📜 License & Credits
* Developed as a production-grade template.
* Under MIT License.
