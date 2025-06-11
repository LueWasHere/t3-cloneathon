<<<<<<< HEAD
// static/js/chat.js

import { escapeHtml } from './ui.js';

let isFirstMessage = true;

// DOM elements can be fetched inside the functions that use them
// to keep this module self-contained.

function formatBotMessage(content) {
    let formatted = content;
    formatted = formatted.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, language, code) => {
        const lang = language ? ` class="language-${language}"` : '';
        return `<pre><code${lang}>${escapeHtml(code.trim())}</code></pre>`;
    });
    formatted = formatted.replace(/`([^`\n]+)`/g, '<code>$1</code>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/_([^_\n]+)_/g, '<em>$1</em>');
    formatted = formatted.replace(/~~(.*?)~~/g, '<del>$1</del>');
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    formatted = formatted.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    formatted = formatted.replace(/^[\-\*] (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    formatted = formatted.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>(?:(?!<\/li><li>).)*<\/li>(?:\s*<li>(?:(?!<\/li><li>).)*<\/li>)*)/gs, '<ol>$1</ol>');
    formatted = formatted.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
    formatted = formatted.replace(/^(---|\*\*\*)$/gm, '<hr>');
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    if (!formatted.startsWith('<')) formatted = '<p>' + formatted + '</p>';
    formatted = formatted.replace(/<p><\/p>/g, '');
    return formatted;
}


function addMessage(content, isUser = false) {
    const messagesContainer = document.getElementById('chatMessages');
    if (isFirstMessage) {
        const welcomeContainer = document.getElementById('welcomeContainer');
        if (welcomeContainer) welcomeContainer.style.display = 'none';
        isFirstMessage = false;
    }
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isUser) {
        contentDiv.textContent = content;
    } else {
        if (content.type === 'image' && content.images && content.images.length > 0) {
            contentDiv.innerHTML = `<img src="${content.images[0]}" alt="Generated image" class="generated-image">`;
        } else if (content.type === 'video' && content.videos && content.videos.length > 0) {
            contentDiv.innerHTML = `<video src="${content.videos[0]}" class="generated-video" controls autoplay loop muted></video>`;
        } else {
            contentDiv.innerHTML = formatBotMessage(content.response || content.error || 'An unexpected error occurred.');
        }
    }

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showLoadingDots() {
    const messagesContainer = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'loadingMessage';
    const dotsDiv = document.createElement('div');
    dotsDiv.className = 'loading-dots';
    dotsDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    loadingDiv.appendChild(dotsDiv);
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeLoadingDots() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) loadingMessage.remove();
}

export async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    if (!message) return;

    // Get the currently selected model from the DOM
    const modelSelector = document.querySelector('.model-selector');
    const selectedModel = modelSelector.dataset.model;
    const currentMediaType = modelSelector.dataset.mediaType || 'llm';

    addMessage(message, true);
    input.value = '';
    handleInput(); // Resize input and update send button state
    showLoadingDots();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                message: message, 
                model: selectedModel,
                mediaType: currentMediaType
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        removeLoadingDots();

        if (data.error) {
            addMessage({ response: `❌ ${data.error}`, type: 'text' }, false);
        } else {
            addMessage(data, false); // Pass the whole data object
        }

    } catch (error) {
        removeLoadingDots();
        addMessage({ response: `An error occurred: ${error.message}`, type: 'text'}, false);
    }
}

export function handleInput() {
    const textarea = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    sendBtn.disabled = textarea.value.trim() === '';
}

export function handleKeyboardShortcuts(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!document.getElementById('sendBtn').disabled) {
            sendMessage();
        }
    }
}

export function sendSampleQuestion(question) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = question;
    handleInput();
    sendMessage();
}

export function startNewChat() {
    const chatMessages = document.getElementById('chatMessages');
    const welcomeContainerHTML = `
        <div class="welcome-container" id="welcomeContainer">
            <h1 class="welcome-title">How can I help you, {{ current_user.name.split(' ')[0] }}?</h1>
             <div class="action-buttons">
                <button class="action-btn" data-action="create"><svg class="icon" viewBox="0 0 24 24"><path d="M9 13h6v-2H9v2zm0-4h6V7H9v2zm0 8h6v-2H9v2zm-7-9v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-6L10 4H4c-1.1 0-2 .9-2 2z"/></svg>Create</button>
                <button class="action-btn" data-action="explore"><svg class="icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>Explore</button>
                <button class="action-btn" data-action="code"><svg class="icon" viewBox="0 0 24 24"><path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/></svg>Code</button>
                <button class="action-btn" data-action="learn"><svg class="icon" viewBox="0 0 24 24"><path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82zM12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/></svg>Learn</button>
            </div>
            <div class="sample-questions">
                <div class="sample-question" data-question="How does AI work?">How does AI work?</div>
                <div class="sample-question" data-question="Are black holes real?">Are black holes real?</div>
                <div class="sample-question" data-question='How many Rs are in the word "strawberry"?'>How many Rs are in the word "strawberry"?</div>
                <div class="sample-question" data-question="What is the meaning of life?">What is the meaning of life?</div>
            </div>
        </div>`;
    chatMessages.innerHTML = welcomeContainerHTML;
    isFirstMessage = true;
    handleInput();
=======
// static/js/chat.js

import { escapeHtml } from './ui.js';

let isFirstMessage = true;

// DOM elements can be fetched inside the functions that use them
// to keep this module self-contained.

function formatBotMessage(content) {
    let formatted = content;
    formatted = formatted.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, language, code) => {
        const lang = language ? ` class="language-${language}"` : '';
        return `<pre><code${lang}>${escapeHtml(code.trim())}</code></pre>`;
    });
    formatted = formatted.replace(/`([^`\n]+)`/g, '<code>$1</code>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/_([^_\n]+)_/g, '<em>$1</em>');
    formatted = formatted.replace(/~~(.*?)~~/g, '<del>$1</del>');
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    formatted = formatted.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    formatted = formatted.replace(/^[\-\*] (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    formatted = formatted.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>(?:(?!<\/li><li>).)*<\/li>(?:\s*<li>(?:(?!<\/li><li>).)*<\/li>)*)/gs, '<ol>$1</ol>');
    formatted = formatted.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
    formatted = formatted.replace(/^(---|\*\*\*)$/gm, '<hr>');
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    if (!formatted.startsWith('<')) formatted = '<p>' + formatted + '</p>';
    formatted = formatted.replace(/<p><\/p>/g, '');
    return formatted;
}


function addMessage(content, isUser = false) {
    const messagesContainer = document.getElementById('chatMessages');
    if (isFirstMessage) {
        const welcomeContainer = document.getElementById('welcomeContainer');
        if (welcomeContainer) welcomeContainer.style.display = 'none';
        isFirstMessage = false;
    }
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isUser) {
        contentDiv.textContent = content;
    } else {
        if (content.type === 'image') {
            contentDiv.innerHTML = `<img src="${content.response}" alt="Generated image" class="generated-image">`;
        } else {
            contentDiv.innerHTML = formatBotMessage(content.response);
        }
    }

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showLoadingDots() {
    const messagesContainer = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'loadingMessage';
    const dotsDiv = document.createElement('div');
    dotsDiv.className = 'loading-dots';
    dotsDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    loadingDiv.appendChild(dotsDiv);
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeLoadingDots() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) loadingMessage.remove();
}

export async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    if (!message) return;

    // Get the currently selected model from the DOM
    const modelSelector = document.querySelector('.model-selector');
    const selectedModel = modelSelector.dataset.model;
    const currentMediaType = modelSelector.dataset.mediaType || 'llm';

    addMessage(message, true);
    input.value = '';
    handleInput(); // Resize input and update send button state
    showLoadingDots();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                message: message, 
                model: selectedModel,
                mediaType: currentMediaType
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        removeLoadingDots();

        if (data.error) {
            addMessage({ response: `❌ ${data.error}`, type: 'text' }, false);
        } else {
            addMessage(data, false); // Pass the whole data object
        }

    } catch (error) {
        removeLoadingDots();
        addMessage({ response: `An error occurred: ${error.message}`, type: 'text'}, false);
    }
}

export function handleInput() {
    const textarea = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    sendBtn.disabled = textarea.value.trim() === '';
}

export function handleKeyboardShortcuts(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!document.getElementById('sendBtn').disabled) {
            sendMessage();
        }
    }
}

export function sendSampleQuestion(question) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = question;
    handleInput();
    sendMessage();
}

export function startNewChat() {
    const chatMessages = document.getElementById('chatMessages');
    const welcomeContainerHTML = `
        <div class="welcome-container" id="welcomeContainer">
            <h1 class="welcome-title">How can I help you, {{ current_user.name.split(' ')[0] }}?</h1>
             <div class="action-buttons">
                <button class="action-btn" data-action="create"><svg class="icon" viewBox="0 0 24 24"><path d="M9 13h6v-2H9v2zm0-4h6V7H9v2zm0 8h6v-2H9v2zm-7-9v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-6L10 4H4c-1.1 0-2 .9-2 2z"/></svg>Create</button>
                <button class="action-btn" data-action="explore"><svg class="icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>Explore</button>
                <button class="action-btn" data-action="code"><svg class="icon" viewBox="0 0 24 24"><path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/></svg>Code</button>
                <button class="action-btn" data-action="learn"><svg class="icon" viewBox="0 0 24 24"><path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82zM12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/></svg>Learn</button>
            </div>
            <div class="sample-questions">
                <div class="sample-question" data-question="How does AI work?">How does AI work?</div>
                <div class="sample-question" data-question="Are black holes real?">Are black holes real?</div>
                <div class="sample-question" data-question='How many Rs are in the word "strawberry"?'>How many Rs are in the word "strawberry"?</div>
                <div class="sample-question" data-question="What is the meaning of life?">What is the meaning of life?</div>
            </div>
        </div>`;
    chatMessages.innerHTML = welcomeContainerHTML;
    isFirstMessage = true;
    handleInput();
>>>>>>> 8d3172731d5e6e3861efbcbb51bc008a999da776
}