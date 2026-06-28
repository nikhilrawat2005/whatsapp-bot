# 🚀 Production Deployment Guide

This document describes how to deploy the Hospital Appointment Booking WhatsApp Bot application to production, focusing on the **Render** cloud platform.

---

## 1. Prerequisites
Before beginning the deployment, make sure you have:
* A GitHub repository with this code pushed.
* A Render Account ([render.com](https://render.com)).
* A PostgreSQL Database instance (automatically provisioned if using the Render Blueprint).
* Meta Developer Credentials (see [META_SETUP.md](META_SETUP.md)).

---

## 2. Render Blueprint Deploy (Recommended)
This repository contains a pre-configured `render.yaml` file that sets up both the database and web service in one click.

### Steps:
1. Log into your **Render Dashboard**.
2. Click **New** (top right) ➔ **Blueprint**.
3. Select and connect your GitHub repository.
4. Render will read `render.yaml` and prompt you to name your service group.
5. Provide values for the required environment variables:
   * `SECRET_KEY`: A secure random string for Flask sessions.
   * `SESSION_SECRET`: An additional session secret key.
   * `WHATSAPP_TOKEN`: Your Meta Permanent System User Access Token.
   * `WHATSAPP_PHONE_NUMBER_ID`: Your Meta WhatsApp Phone Number ID.
   * `WHATSAPP_VERIFY_TOKEN`: A token of your choice used to verify the webhook handshake.
6. Click **Approve**. Render will provision:
   * A private **PostgreSQL** database.
   * A **Flask Python Web Service** running behind Gunicorn.

---

## 3. Manual Deployment on Render
If you prefer to configure the components manually without a Blueprint:

### Step 3.1: Create a PostgreSQL Database
1. In the Render Dashboard, click **New** ➔ **PostgreSQL**.
2. Name the database, select a region, and choose the Free or starter tier.
3. Click **Create Database**.
4. Once active, copy the **Internal Database URL** (for Render to Render connection) or **External Database URL**.

### Step 3.2: Create a Flask Web Service
1. Click **New** ➔ **Web Service**.
2. Connect your GitHub repository.
3. Set the following parameters:
   * **Name**: `hospital-booking-bot`
   * **Environment**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
4. Expand **Advanced** and add the Environment Variables (see [ENVIRONMENT.md](ENVIRONMENT.md)). Include the `DATABASE_URL` copied from Step 3.1.
5. Click **Create Web Service**.

---

## 4. Production Verifications
* Once the build completes, Render will provide a public URL like `https://hospital-booking-bot.onrender.com`.
* Access the URL to verify the Hospital website is working.
* Access `https://your-service.onrender.com/admin` to see the Admin Dashboard.
* Register the webhook on the Meta Developer Console pointing to `https://your-service.onrender.com/webhook` (refer to [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md)).
