# 💬 Meta WhatsApp Cloud API Setup Guide

This guide details how to configure a production-level Meta Developer Account to connect the Hospital Booking Bot with the WhatsApp Business Platform.

---

## 1. Creating a Meta App
1. Go to the [Meta Developers Console](https://developers.facebook.com/).
2. Log in and click **My Apps** ➔ **Create App**.
3. Choose **Other** for the app type, then click **Next**.
4. Choose **Business** as the app category. Click **Next**.
5. Fill in the App Display Name (e.g. `Hospital Booking Bot`) and select/create a Business Manager account.
6. Click **Create App**.

---

## 2. Setting Up the WhatsApp Product
1. From the App Dashboard, locate **WhatsApp** under the list of products and click **Set up**.
2. Select or create your Business Account profile and click **Continue**.
3. You will be redirected to the **Getting Started** panel.
   * Note the temporary access token (valid for 24 hours) for initial test runs.
   * Copy the **Phone Number ID** (e.g. `102938475610293`), which is required for the `WHATSAPP_PHONE_NUMBER_ID` environment variable.

---

## 3. Registering Test Recipient Numbers
Before your WhatsApp Business Account is fully verified, you can only send messages to pre-registered test numbers:
1. Under **Send and receive messages**, select the **To** field.
2. Click the dropdown and select **Manage phone numbers list**.
3. Add your personal WhatsApp number with country code.
4. Input the verification code sent to your phone.

---

## 4. Generating a Permanent Access Token
Temporary tokens expire after 24 hours. For production deployments:
1. Go to the [Facebook Business Suite Settings](https://business.facebook.com/settings/).
2. Choose your business manager and go to **Users** ➔ **System Users**.
3. Click **Add** to create a new System User. Assign the **Admin** role.
4. Select the system user, click **Add Assets**, choose **Apps**, select your WhatsApp App, and toggle on **Full Control**. Save changes.
5. Click **Generate New Token**.
6. Select your WhatsApp App and check the boxes for:
   * `whatsapp_business_messaging`
   * `whatsapp_business_management`
7. Click **Generate Token**. Copy this token immediately and save it as `WHATSAPP_TOKEN` in your env config.

---

## 5. Moving to Production Number
To launch with a real business number:
1. Go to the **WhatsApp** ➔ **Getting Started** section in your App Dashboard.
2. Scroll to the bottom and click **Add Phone Number**.
3. Fill in your business profile details, name, and register a new phone number.
4. Verify the number via SMS or voice call.
5. Update your `WHATSAPP_PHONE_NUMBER_ID` with the new production ID generated for this number.
