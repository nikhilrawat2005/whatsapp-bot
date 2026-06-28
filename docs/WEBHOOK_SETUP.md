# 🔗 Webhook Setup and Verification Guide

This guide explains how to connect Meta's real-time events to the Hospital Booking Bot webhook.

---

## 1. Webhook Endpoint Specification
The webhook routing endpoint in the Flask application is located at:
`https://<your-domain>/webhook`

It handles two methods:
* **GET**: Used by Meta during the verification handshake.
* **POST**: Used by Meta to push real-time user chat messages.

---

## 2. Setting Up Webhook Verification
1. On the Meta Developer Portal, expand **WhatsApp** on the left menu and select **Configuration**.
2. Click **Edit** next to **Webhook**.
3. Fill in:
   * **Callback URL**: `https://<your-deployed-domain>.onrender.com/webhook` (or your Ngrok forwarding address for local testing, e.g. `https://xxxx.ngrok-free.app/webhook`).
   * **Verify Token**: Provide a secure string of your choice. This must match the `WHATSAPP_VERIFY_TOKEN` defined in your environment configuration (default fallback: `abc_hospital_verify_token_123`).
4. Click **Verify and Save**. Meta will send a GET request to your webhook with the token. If it matches, the webhook becomes active.

---

## 3. Subscribing to Message Events
Once the webhook is successfully verified, you must subscribe to message events:
1. On the WhatsApp Configuration page, find **Webhook fields**.
2. Click **Manage**.
3. Locate **messages** in the field list and click **Subscribe**.
4. Click **Done**.

The bot will now receive a JSON payload containing the sender's phone number and the message text whenever a user messages your WhatsApp Business number.
