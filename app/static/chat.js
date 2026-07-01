/**
 * Web Chat Client-Side JavaScript
 * Handles floating chat widget interactions, UI states, and REST API communications.
 */

// Global variables
let sessionKey = null;
let chatOpened = false;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // Check if session key already exists in localStorage, otherwise create one
    sessionKey = localStorage.getItem('hospital_chat_session_key');
    if (!sessionKey) {
        sessionKey = generateUUID();
        localStorage.setItem('hospital_chat_session_key', sessionKey);
    }
    
    // Initialize the chat session
    initChatSession();
});

// Helper: Generate UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        let r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Toggle chat widget view
function toggleChat() {
    const chatWidget = document.getElementById('chatWidget');
    const chatFabIcon = document.getElementById('chatFabIcon');
    const chatFabClose = document.getElementById('chatFabClose');
    const chatFabBadge = document.getElementById('chatFabBadge');
    
    chatOpened = !chatOpened;
    
    if (chatOpened) {
        chatWidget.classList.add('open');
        chatFabIcon.classList.add('hidden');
        chatFabClose.classList.remove('hidden');
        if (chatFabBadge) chatFabBadge.classList.add('hidden');
        
        // If message list is empty, initialize session from backend
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages.children.length === 0) {
            initChatSession();
        } else {
            scrollToBottom();
        }
    } else {
        chatWidget.classList.remove('open');
        chatFabIcon.classList.remove('hidden');
        chatFabClose.classList.add('hidden');
    }
}

// Open chat widget explicitly
function openChat() {
    if (!chatOpened) {
        toggleChat();
    }
}

// Close chat widget explicitly
function closeChat() {
    if (chatOpened) {
        toggleChat();
    }
}

// Initialize chat session from API
async function initChatSession() {
    showTypingIndicator();
    try {
        const response = await fetch('/api/chat/init', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_key: sessionKey })
        });
        const data = await response.json();
        hideTypingIndicator();
        
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = ''; // Clear previous messages
        
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => addMessage(msg, 'bot'));
        }
        
        renderButtons(data.buttons || []);
        updateInputState(data.input);
    } catch (error) {
        console.error('Error initializing chat:', error);
        hideTypingIndicator();
        addMessage('Welcome to ABC Hospital! 👋 How can I help you today?', 'bot');
        renderButtons(['📅 Book Appointment', '🏥 Departments', '📍 Hospital Info']);
    }
}

// Reset/restart the entire chat session
async function resetChat() {
    if (confirm('Are you sure you want to restart the conversation? All progress will be lost.')) {
        sessionKey = generateUUID();
        localStorage.setItem('hospital_chat_session_key', sessionKey);
        await initChatSession();
    }
}

// Render message in chat window
function addMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'bot' ? 'bot-message' : 'user-message');
    
    // Support basic markdown-like newline formatting
    const formattedText = text.replace(/\n/g, '<br>');
    msgDiv.innerHTML = `<div class="message-bubble">${formattedText}</div>`;
    
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
}

// Render quick action buttons
function renderButtons(buttons) {
    const chatButtons = document.getElementById('chatButtons');
    chatButtons.innerHTML = '';
    
    if (!buttons || buttons.length === 0) return;
    
    buttons.forEach(btnLabel => {
        const btn = document.createElement('button');
        btn.classList.add('chat-btn');
        btn.textContent = btnLabel;
        btn.onclick = () => sendChatMessage(btnLabel);
        chatButtons.appendChild(btn);
    });
}

// Handle dynamic input state/placeholder changes from backend
function updateInputState(inputConfig) {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;
    
    if (inputConfig) {
        chatInput.type = inputConfig.type || 'text';
        chatInput.placeholder = inputConfig.placeholder || 'Type your message…';
        chatInput.disabled = false;
    } else {
        chatInput.type = 'text';
        chatInput.placeholder = 'Type your message…';
        chatInput.disabled = false;
    }
}

// Show loading typing indicator
function showTypingIndicator() {
    hideTypingIndicator(); // Ensure no duplicates
    const chatMessages = document.getElementById('chatMessages');
    const indicatorDiv = document.createElement('div');
    indicatorDiv.id = 'typingIndicator';
    indicatorDiv.classList.add('message', 'bot-message');
    indicatorDiv.innerHTML = `
        <div class="message-bubble typing-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(indicatorDiv);
    scrollToBottom();
}

// Hide loading typing indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// Scroll chat to bottom
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send chat message triggered from input box
function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const text = chatInput.value.trim();
    if (!text) return;
    
    chatInput.value = '';
    sendChatMessage(text);
}

// Send chat message to backend
async function sendChatMessage(text) {
    // Add user message to UI
    addMessage(text, 'user');
    
    // Clear current quick buttons
    document.getElementById('chatButtons').innerHTML = '';
    
    // Show typing loader
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_key: sessionKey,
                message: text
            })
        });
        
        const data = await response.json();
        hideTypingIndicator();
        
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => addMessage(msg, 'bot'));
        }
        
        renderButtons(data.buttons || []);
        updateInputState(data.input);
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessage('Sorry, I encountered an issue. Let\'s return to the main menu.', 'bot');
        renderButtons(['🏠 Main Menu']);
    }
}

// Handle Enter keypress in input box
function handleInputKey(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}
