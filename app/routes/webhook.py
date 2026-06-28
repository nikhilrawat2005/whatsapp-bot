import logging
from flask import Blueprint, request, jsonify
from app.config import Config
from app.services import bot_service

logger = logging.getLogger(__name__)
webhook_bp = Blueprint('webhook_api', __name__)

@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """Webhook verification endpoint required by Meta Developer Console."""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == Config.WHATSAPP_VERIFY_TOKEN:
            logger.info("Meta Webhook verified successfully.")
            return challenge, 200
        else:
            logger.warning("Webhook verification attempt failed due to invalid token.")
            return "Forbidden", 403
    return "Not Found", 404

@webhook_bp.route('/webhook', methods=['POST'])
def receive_message():
    """Handles incoming message payloads sent from Meta WhatsApp servers."""
    if not request.is_json:
        logger.warning("Received webhook request with non-JSON content type.")
        return jsonify({"error": "Bad Request: Content-Type must be application/json"}), 400
        
    try:
        data = request.get_json()
    except Exception as e:
        logger.error(f"Error parsing incoming JSON webhook payload: {e}")
        return jsonify({"error": "Bad Request: Invalid JSON"}), 400

    logger.debug(f"Incoming webhook payload: {data}")
    
    if not data:
        return jsonify({"status": "ignored", "reason": "empty payload"}), 200
        
    try:
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    for message in messages:
                        phone_number = message.get('from')
                        
                        # Capture message body/interaction content
                        message_text = ""
                        if 'text' in message:
                            message_text = message['text'].get('body', '')
                        elif 'button' in message:
                            message_text = message['button'].get('text', '')
                        elif 'interactive' in message:
                            interactive = message['interactive']
                            if interactive.get('type') == 'button_reply':
                                message_text = interactive['button_reply'].get('title', '')
                                
                        if phone_number and message_text:
                            logger.info(f"Received chatbot message from {phone_number}: {message_text}")
                            # Route message down to the Bot state service machine
                            bot_service.handle_incoming_message(phone_number, message_text)
    except Exception as e:
        logger.error(f"Unexpected error processing webhook data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
                        
    return jsonify({"status": "success"}), 200
