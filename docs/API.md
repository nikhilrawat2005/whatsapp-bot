# 🔌 API Endpoint Documentation

This document describes the API endpoints exposed by the Hospital Appointment Booking System.

---

## 1. Webhook Handshake Verification
Used by Meta Developer Portal to verify that the webhook belongs to your app.

* **Endpoint**: `/webhook`
* **Method**: `GET`
* **Query Parameters**:
  * `hub.mode`: Required (Must be `subscribe`).
  * `hub.verify_token`: Required (Must match `WHATSAPP_VERIFY_TOKEN`).
  * `hub.challenge`: Required (Returned back as plain text on successful match).

* **Response**:
  * **Success (200 OK)**: Returns the `hub.challenge` string.
  * **Unauthorized (403 Forbidden)**: `"Forbidden"` (if verify token does not match).
  * **Bad Request (404 Not Found)**: `"Not Found"` (if query parameters are missing).

---

## 2. Webhook Event Notifications
Receives real-time updates and incoming user messages pushed by Meta WhatsApp Cloud servers.

* **Endpoint**: `/webhook`
* **Method**: `POST`
* **Content-Type**: `application/json`
* **Payload Structure Example**:
  ```json
  {
    "object": "whatsapp_business_account",
    "entry": [
      {
        "id": "123456789012345",
        "changes": [
          {
            "value": {
              "messaging_product": "whatsapp",
              "metadata": {
                "display_phone_number": "15550000000",
                "phone_number_id": "102938475610293"
              },
              "messages": [
                {
                  "from": "15551234567",
                  "id": "wamid.HBgLMTU1NTEyMzQ1NjcVAgASGBQzQTdDNEM1Nzg5QkFDREQ1RUJBMgA=",
                  "timestamp": "1672531199",
                  "text": {
                    "body": "Hello"
                  },
                  "type": "text"
                }
              ]
            },
            "field": "messages"
          }
        ]
      }
    ]
  }
  ```

* **Response**:
  * **Success (200 OK)**: `{"status": "success"}` or `{"status": "ignored"}`
  * **Invalid Request (400 Bad Request)**: `{"error": "Bad Request: Content-Type must be application/json"}` / `{"error": "Bad Request: Invalid JSON"}`
  * **Server Error (500 Internal Server Error)**: `{"error": "Internal Server Error"}`
