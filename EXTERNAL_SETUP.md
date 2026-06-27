# External Setup Guide (WhatsApp & Webhook Configuration)

This document provides a step-by-step guide on how to configure the external services required for this WhatsApp Bot to work correctly.

---

## Step 1: Create a Meta Developer Account and App
1. Go to the [Meta Developers Portal](https://developers.facebook.com/) and register for a developer account if you don't have one.
2. Click on **My Apps** and then **Create App**.
3. Select **Other** as the use case, click **Next**.
4. Select **Business** as the app type, click **Next**.
5. Give your app a name (e.g., `Hospital Booking Bot`) and select your Business Manager account (or leave it default/create one).
6. Click **Create App** and enter your password.

---

## Step 2: Add WhatsApp to Your App
1. On the App Dashboard, scroll down to find **WhatsApp** and click **Set up**.
2. If prompted, select or create a Business Profile / Business Account and click **Continue**.
3. You will be redirected to the WhatsApp **Getting Started** page.
   - Here, Meta will generate a **Temporary Access Token** (valid for 24 hours).
   - You will also see a **Test Phone Number** and a **Phone Number ID**. Copy the **Phone Number ID** to use as `WHATSAPP_PHONE_NUMBER_ID` in your `.env` file.

---

## Step 3: Add Test Recipient Numbers
Since the app is in Development Mode:
1. On the **Getting Started** page, look for the **To** field under "Send and receive messages".
2. Add your own personal WhatsApp phone number to register it as a test recipient.
3. Follow the verification steps (Meta will send a verification code to your WhatsApp).
4. Send a test template message from the Meta console to verify the connection.

---

## Step 4: Generate a Permanent Access Token (Highly Recommended)
Temporary Access Tokens expire in 24 hours. For a production-ready application:
1. Go to your Facebook Business Manager: [https://business.facebook.com/](https://business.facebook.com/).
2. Navigate to **Business Settings** ➔ **Users** ➔ **System Users**.
3. Click **Add** to create a new System User. Select role as **Admin**.
4. Select the newly created system user and click **Add Assets**.
5. Under **Apps**, select your WhatsApp App, enable **Full Control (Manage App)**, and save changes.
6. Click **Generate New Token**, select your WhatsApp App.
7. Check the boxes for **whatsapp_business_messaging** and **whatsapp_business_management**.
8. Click **Generate Token**. Copy this token immediately and save it safely. This is your permanent `WHATSAPP_TOKEN`.

---

## Step 5: Start a Local Tunnel (Ngrok) for Local Webhook
WhatsApp needs a public `https` URL to send webhook events (incoming messages) to your local server.
1. Download and install [Ngrok](https://ngrok.com/).
2. Run your Flask app locally (it runs on port `5000` by default):
   ```bash
   python app.py
   ```
3. In a separate terminal, start Ngrok to forward port 5000:
   ```bash
   ngrok http 5000
   ```
4. Ngrok will output a public URL looking like: `https://xxxx-xxxx-xxxx.ngrok-free.app`.
   - Copy this URL. Your webhook handler path is `/webhook`, so your full webhook URL is `https://xxxx-xxxx-xxxx.ngrok-free.app/webhook`.

---

## Step 6: Configure Meta Webhooks
1. In the Meta Developer Portal, go to the left sidebar and expand **WhatsApp** ➔ **Configuration**.
2. Click **Edit** next to **Webhook**.
3. Enter your Webhook URL:
   - **Callback URL**: `https://xxxx-xxxx-xxxx.ngrok-free.app/webhook` (replace with your active Ngrok URL)
   - **Verify Token**: `abc_hospital_verify_token_123` (this must match the `WHATSAPP_VERIFY_TOKEN` in your `.env` file)
4. Click **Verify and Save**.
5. Under **Webhook fields**, click **Manage** and subscribe to **messages** (critical for receiving incoming messages).

---

## Step 7: Local Environment Setup
Create a file named `.env` in the root folder (use `.env.example` as a template) and configure:
```env
PORT=5000
SECRET_KEY=any-secure-random-string
FLASK_ENV=development
# System defaults to sqlite:///hospital.db locally if DATABASE_URL is not specified
DATABASE_URL=sqlite:///hospital.db 

WHATSAPP_TOKEN=your_meta_access_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=abc_hospital_verify_token_123
```
