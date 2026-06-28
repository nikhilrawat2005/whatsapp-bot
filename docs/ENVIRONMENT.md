# ⚙️ Environment Variables Configuration Guide

The application uses environment variables to load configurations dynamically. These settings reside in a `.env` file in the root directory for local development, and in the environment configurations panel for cloud platforms (e.g. Render).

---

## 1. Required Variables

| Name | Expected Value | Default Fallback (Local Development Only) | Description |
|---|---|---|---|
| `PORT` | Integer (e.g. `5000`) | `5000` | Port on which the Flask server runs. |
| `FLASK_ENV` | `development` / `production` | `production` | Flask running environment setting. |
| `SECRET_KEY` | Random String | `abc-hospital-session-secret-key-9988` | Key used for cryptographically signing Flask sessions. |
| `SESSION_SECRET` | Random String | Matches `SECRET_KEY` | Additional key for cryptographic security. |
| `DATABASE_URL` | Connection URI | `sqlite:///hospital.db` | PostgreSQL or SQLite connection endpoint URI. |
| `WHATSAPP_TOKEN` | System Access Token | `""` | Permanent Access Token generated on the Meta Business Portal. |
| `WHATSAPP_PHONE_NUMBER_ID` | Numeric String | `""` | Meta-assigned WhatsApp Phone Number ID. |
| `WHATSAPP_VERIFY_TOKEN` | String | `abc_hospital_verify_token_123` | Security handshake token for the webhook setup. |

---

## 2. Setting Up Variables

### 2.1 Local Setup
Copy the configuration template from the root folder:
```bash
copy .env.example .env
```
Fill in the values in your new `.env` file. The application automatically loads this file at startup.

### 2.2 Production Setup (Render)
1. Navigate to your Web Service in the **Render Dashboard**.
2. Go to the **Environment** tab.
3. Click **Add Environment Variable**.
4. Define the variables from the table above.
5. Click **Save Changes**. Render will automatically restart your server with the new environment values loaded.
