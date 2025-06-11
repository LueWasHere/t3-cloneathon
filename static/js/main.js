// static/js/main.js - CORRECTED

import { initializeTheme, toggleTheme } from './ui.js';
import { sendMessage, sendSampleQuestion, startNewChat, handleInput, handleKeyboardShortcuts } from './chat.js';
import { toggleModelPopover, togglePopoverExpandedView, initializePopoverSearch, switchMediaType } from './popover.js';

// --- App State ---
const state = {
    selectedModel: 'Gemini 2.5 Flash',
    selectedProvider: 'google',
    selectedApiName: 'gemini-2.5-flash-preview-05-20',
    currentMediaType: 'llm',
};

// --- App Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Basic UI setup
    initializeTheme();
    
    // Set initial model state on the DOM for other modules to access
    const modelSelector = document.querySelector('.model-selector');
    modelSelector.dataset.model = state.selectedModel;
    modelSelector.dataset.provider = state.selectedProvider;
    modelSelector.dataset.apiName = state.selectedApiName;
    modelSelector.dataset.mediaType = state.currentMediaType;
    document.getElementById('selectedModelName').textContent = state.selectedModel;
    
    // *** THE FIX IS HERE: The problematic line below has been removed. ***
    // document.getElementById('selectedModelApiName').textContent = state.selectedApiName; // <-- This line caused the error and is now gone.
    
    // Attach all event listeners
    // Header
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Sidebar
    document.querySelector('.new-chat-btn').addEventListener('click', startNewChat);

    // Main Chat Area & Input
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('messageInput').addEventListener('input', handleInput);
    document.getElementById('messageInput').addEventListener('keydown', handleKeyboardShortcuts);

    document.getElementById('chatMessages').addEventListener('click', (event) => {
        const sampleQuestionEl = event.target.closest('.sample-question');
        if (sampleQuestionEl) {
            sendSampleQuestion(sampleQuestionEl.dataset.question);
        }
        const actionBtnEl = event.target.closest('.action-btn');
        if (actionBtnEl) {
             alert(`Action button "${actionBtnEl.dataset.action}" clicked. Functionality not implemented.`);
        }
    });

    // Model Popover
    modelSelector.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleModelPopover();
    });
    document.getElementById('modelDropdownOverlay').addEventListener('click', toggleModelPopover);
    document.getElementById('popoverShowMoreBtn').addEventListener('click', togglePopoverExpandedView);
    initializePopoverSearch();
    
    document.querySelectorAll('.media-type-btn').forEach(btn => {
        btn.addEventListener('click', () => switchMediaType(btn.dataset.type));
    });

    // Initial state setup
    handleInput();
    startNewChat();
});