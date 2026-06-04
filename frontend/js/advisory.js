// ============================================================
// advisory.js — AI Business Advisory Chatbot Logic
//
// Manages the full chatbot interface on the advisory page:
//
// - sendMessage()          : Sends user input to Claude AI
// - appendMessage()        : Adds a message bubble to the chat
// - showTypingIndicator()  : Shows animated dots while waiting
// - removeTypingIndicator(): Removes dots when response arrives
// - handleKeyPress()       : Send message on Enter key
// - useSuggestion()        : Fill input from a chip and send
// - clearChat()            : Reset the entire conversation
//
// Conversation history is stored in the `conversationHistory`
// array and sent with every request so Claude remembers
// what was said earlier in the session.
// ============================================================

// Base URL for all API calls
var API_BASE = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') ? 'http://localhost:5000' : 'https://bizanalytics-production-66f5.up.railway.app'
    ? 'http://127.0.0.1:5000/api'
    : 'https://bizanalytics-production-66f5.up.railway.app/api';

// Stores the full conversation history for multi-turn memory.
// Each item: { role: 'user' | 'assistant', content: '...' }
let conversationHistory = [];


// ── Send Message ──────────────────────────────────────────────
// Called when the user clicks Send or presses Enter.
// Sends the message and history to the backend Claude endpoint.
async function sendMessage() {
    const input   = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;  // Ignore empty sends

    // Show the user's message in the chat window
    appendMessage('user', message);
    input.value = '';  // Clear input field

    // Add to history BEFORE sending (for context in next turn)
    conversationHistory.push({ role: 'user', content: message });

    // Show animated typing indicator while waiting for AI response
    const typingId = showTypingIndicator();

    try {
        // Send message + full history to backend advisory endpoint
        const res = await fetch(`${API_BASE}/advisory/chat`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                message: message,
                // Send history excluding the current message
                // (backend appends it before calling Claude)
                history: conversationHistory.slice(0, -1)
            })
        });

        const data = await res.json();

        // Remove typing dots before showing AI reply
        removeTypingIndicator(typingId);

        if (res.ok) {
            // Display AI response in the chat window
            appendMessage('bot', data.reply);

            // Add AI reply to history for next turn memory
            conversationHistory.push({
                role:    'assistant',
                content: data.reply
            });
        } else {
            appendMessage('bot',
                `Sorry, I encountered an error: ${data.error}`);
        }

    } catch (err) {
        removeTypingIndicator(typingId);
        appendMessage('bot',
            'I could not connect to the server. ' +
            'Please make sure the backend is running.');
    }
}


// ── Append Message to Chat Window ────────────────────────────
// Creates a new styled message bubble and adds it to the chat.
// Bot messages are on the left; user messages on the right.
function appendMessage(role, text) {
    const chatBox    = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');

    // Add correct CSS classes based on who sent the message
    messageDiv.classList.add(
        'message',
        role === 'user' ? 'user-message' : 'bot-message'
    );

    // Choose Font Awesome icon for the avatar
    const icon = role === 'user' ? 'fa-user' : 'fa-robot';

    // Format bot responses: convert **bold** and newlines to HTML
    const formattedText = role === 'bot'
        ? text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
        : text;

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${icon}"></i>
        </div>
        <div class="message-bubble">
            <p>${formattedText}</p>
        </div>
    `;

    chatBox.appendChild(messageDiv);

    // Auto-scroll to the newest message
    chatBox.scrollTop = chatBox.scrollHeight;
}


// ── Show Typing Indicator ─────────────────────────────────────
// Adds an animated three-dot indicator to show Claude is thinking.
// Returns a unique ID so we can find and remove it later.
function showTypingIndicator() {
    const chatBox   = document.getElementById('chat-box');
    const id        = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');

    typingDiv.classList.add('message', 'bot-message');
    typingDiv.id = id;

    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;

    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}


// ── Remove Typing Indicator ───────────────────────────────────
// Finds and removes the typing dots element by its unique ID.
function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}


// ── Handle Enter Key Press ────────────────────────────────────
// Allows sending a message by pressing Enter (not just clicking)
function handleKeyPress(event) {
    if (event.key === 'Enter') sendMessage();
}


// ── Use Suggestion Chip ───────────────────────────────────────
// When a suggestion chip is clicked, fills the input with
// that question text and immediately sends it.
function useSuggestion(btn) {
    const input = document.getElementById('chat-input');
    input.value = btn.textContent.trim();
    sendMessage();
}


// ── Clear Chat ────────────────────────────────────────────────
// Resets the conversation history and restores the welcome message.
// The AI will start fresh without memory of previous messages.
function clearChat() {
    conversationHistory = [];  // Wipe conversation memory

    document.getElementById('chat-box').innerHTML = `
        <div class="message bot-message">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-bubble">
                <p>
                    Hello! I am your AI business advisor powered by Claude.
                    I have access to your uploaded sales data and I am ready
                    to help you make smarter business decisions.
                    You can also ask me to help map your data columns if your
                    file uses different column names.
                    What would you like to know?
                </p>
            </div>
        </div>
    `;
}
