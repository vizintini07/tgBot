// Telegram WebApp SDK initialization
const tg = window.Telegram.WebApp;
tg.expand();
tg.enableClosingConfirmation();

// State management
let userHistory = [];
let conversationHistory = [];
let lastQuestion = '';
let currentGradient = { start: '#2481cc', end: '#1a5a8a' };

// DOM elements
const chatContainer = document.getElementById('chatContainer');
const historyContainer = document.getElementById('historyContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const historyBtn = document.getElementById('historyBtn');
const resetBtn = document.getElementById('resetBtn');
const backBtn = document.getElementById('backBtn');
const chatView = document.getElementById('chatView');
const historyView = document.getElementById('historyView');

// API URL from environment or default
const API_URL = 'API_URL_PLACEHOLDER';

// Initialize
init();

function init() {
    loadHistory();
    setupEventListeners();
    applyTelegramTheme();

    // Remove welcome message if there's conversation history
    if (conversationHistory.length > 0) {
        document.querySelector('.welcome-message')?.remove();
        renderConversation();
    }
}

function setupEventListeners() {
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('keydown', handleKeyDown);
    sendBtn.addEventListener('click', sendMessage);
    historyBtn.addEventListener('click', showHistory);
    backBtn.addEventListener('click', hideHistory);
    resetBtn.addEventListener('click', resetDialog);
}

function handleInputChange() {
    const value = messageInput.value.trim();
    sendBtn.disabled = !value;

    // Auto-resize textarea
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) {
            sendMessage();
        }
    }
}

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // Remove welcome message if it exists
    document.querySelector('.welcome-message')?.remove();

    // Add user message to UI
    addMessage(text, 'user');

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Add to conversation history
    conversationHistory.push({
        question: lastQuestion,
        answer: text
    });

    // Show typing indicator
    const typingIndicator = addTypingIndicator();

    // Send to backend
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: tg.initDataUnsafe?.user?.id || 'webapp_user',
                consversion: conversationHistory
            })
        });

        const data = await response.json();

        // Remove typing indicator
        typingIndicator.remove();

        handleBackendResponse(data);

    } catch (error) {
        console.error('Error:', error);
        typingIndicator.remove();
        addMessage('Произошла ошибка при подключении к серверу. Попробуйте еще раз.', 'bot');
        tg.showAlert('Ошибка подключения к серверу');
    }
}

function handleBackendResponse(data) {
    const { action, text, movie, color } = data;

    // Update gradient if color is provided
    if (color) {
        updateGradient(color);
    }

    if (action === 'ask') {
        // Bot asks another question
        addMessage(text, 'bot');
        lastQuestion = text;

    } else if (action === 'recommend') {
        // Bot recommends a movie
        addMessage(text, 'bot');

        if (movie) {
            addMovieCard(movie);
            saveToHistory(movie);
        }

        // Reset conversation after recommendation
        setTimeout(() => {
            conversationHistory = [];
            lastQuestion = '';
        }, 1000);

    } else {
        // Error or other action
        addMessage(text || 'Что-то пошло не так. Попробуйте еще раз.', 'bot');
    }
}

function addMessage(text, type) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;

    const bubbleEl = document.createElement('div');
    bubbleEl.className = 'message-bubble';
    bubbleEl.textContent = text;

    messageEl.appendChild(bubbleEl);
    chatContainer.appendChild(messageEl);

    scrollToBottom();
}

function addMovieCard(movie) {
    const cardEl = document.createElement('div');
    cardEl.className = 'message bot';

    const movieCard = document.createElement('div');
    movieCard.className = 'movie-card';

    const titleEl = document.createElement('div');
    titleEl.className = 'movie-title';
    titleEl.textContent = `🍿 ${movie.title}`;

    if (movie.year) {
        const yearEl = document.createElement('span');
        yearEl.className = 'movie-year';
        yearEl.textContent = ` (${movie.year})`;
        titleEl.appendChild(yearEl);
    }

    movieCard.appendChild(titleEl);

    if (movie.description) {
        const descEl = document.createElement('div');
        descEl.className = 'movie-description';
        descEl.textContent = movie.description;
        movieCard.appendChild(descEl);
    }

    // Add links
    const links = [];
    if (movie.kp_url) {
        links.push(`<a href="${movie.kp_url}" class="movie-link" target="_blank">Кинопоиск</a>`);
    }
    if (movie.rutube_url) {
        links.push(`<a href="${movie.rutube_url}" class="movie-link" target="_blank">Смотреть на Rutube</a>`);
    }

    if (links.length > 0) {
        const linksEl = document.createElement('div');
        linksEl.className = 'movie-links';
        linksEl.innerHTML = links.join('');
        movieCard.appendChild(linksEl);
    }

    cardEl.appendChild(movieCard);
    chatContainer.appendChild(cardEl);

    scrollToBottom();
}

function addTypingIndicator() {
    const typingEl = document.createElement('div');
    typingEl.className = 'message bot';
    typingEl.id = 'typingIndicator';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    typingEl.appendChild(indicator);
    chatContainer.appendChild(typingEl);

    scrollToBottom();

    return typingEl;
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function updateGradient(color) {
    // Parse color and create gradient
    const startColor = color;
    const endColor = darkenColor(color, 20);

    currentGradient = { start: startColor, end: endColor };

    document.documentElement.style.setProperty('--gradient-start', startColor);
    document.documentElement.style.setProperty('--gradient-end', endColor);
    document.body.style.background = `linear-gradient(135deg, ${startColor} 0%, ${endColor} 100%)`;
}

function darkenColor(color, percent) {
    // Convert hex to RGB
    let r = parseInt(color.slice(1, 3), 16);
    let g = parseInt(color.slice(3, 5), 16);
    let b = parseInt(color.slice(5, 7), 16);

    // Darken
    r = Math.floor(r * (100 - percent) / 100);
    g = Math.floor(g * (100 - percent) / 100);
    b = Math.floor(b * (100 - percent) / 100);

    // Convert back to hex
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

function saveToHistory(movie) {
    userHistory.unshift({
        ...movie,
        timestamp: Date.now()
    });

    // Keep only last 50 movies
    if (userHistory.length > 50) {
        userHistory = userHistory.slice(0, 50);
    }

    localStorage.setItem('movieHistory', JSON.stringify(userHistory));
}

function loadHistory() {
    try {
        const saved = localStorage.getItem('movieHistory');
        if (saved) {
            userHistory = JSON.parse(saved);
        }
    } catch (e) {
        console.error('Error loading history:', e);
    }
}

function showHistory() {
    historyView.classList.add('active');
    renderHistory();
}

function hideHistory() {
    historyView.classList.remove('active');
}

function renderHistory() {
    if (userHistory.length === 0) {
        historyContainer.innerHTML = `
            <div class="empty-history">
                <div class="empty-icon">📽️</div>
                <p>История пока пуста</p>
                <span>Найденные фильмы будут отображаться здесь</span>
            </div>
        `;
        return;
    }

    historyContainer.innerHTML = '';

    userHistory.forEach(movie => {
        const itemEl = document.createElement('div');
        itemEl.className = 'history-item';

        itemEl.innerHTML = `
            <div class="history-item-title">${movie.title}</div>
            ${movie.year ? `<div class="history-item-year">${movie.year}</div>` : ''}
            ${movie.description ? `<div class="history-item-description">${movie.description}</div>` : ''}
        `;

        itemEl.addEventListener('click', () => {
            const links = [];
            if (movie.kp_url) links.push(movie.kp_url);
            if (movie.rutube_url) links.push(movie.rutube_url);

            if (links.length > 0) {
                tg.openLink(links[0]);
            }
        });

        historyContainer.appendChild(itemEl);
    });
}

function resetDialog() {
    tg.showConfirm('Начать новый диалог? Текущая беседа будет очищена.', (confirmed) => {
        if (confirmed) {
            conversationHistory = [];
            lastQuestion = '';
            chatContainer.innerHTML = `
                <div class="welcome-message">
                    <img src="/static/logo.svg" alt="Кинотавр" class="bot-logo">
                    <h2>Привет! Я Кинотавр</h2>
                    <p>Расскажи, какое у тебя сейчас настроение, или чего хочется от фильма на вечер?</p>
                </div>
            `;

            // Reset gradient to default
            updateGradient('#2481cc');

            tg.showPopup({
                message: 'Диалог сброшен. Можете начать заново!'
            });
        }
    });
}

function renderConversation() {
    chatContainer.innerHTML = '';

    conversationHistory.forEach(item => {
        if (item.question) {
            addMessage(item.question, 'bot');
        }
        if (item.answer) {
            addMessage(item.answer, 'user');
        }
    });
}

function applyTelegramTheme() {
    // Apply Telegram theme colors if available
    if (tg.themeParams) {
        const params = tg.themeParams;

        if (params.bg_color) {
            document.documentElement.style.setProperty('--tg-theme-bg-color', params.bg_color);
        }
        if (params.text_color) {
            document.documentElement.style.setProperty('--tg-theme-text-color', params.text_color);
        }
        if (params.hint_color) {
            document.documentElement.style.setProperty('--tg-theme-hint-color', params.hint_color);
        }
        if (params.link_color) {
            document.documentElement.style.setProperty('--tg-theme-link-color', params.link_color);
        }
        if (params.button_color) {
            document.documentElement.style.setProperty('--tg-theme-button-color', params.button_color);
        }
        if (params.button_text_color) {
            document.documentElement.style.setProperty('--tg-theme-button-text-color', params.button_text_color);
        }
        if (params.secondary_bg_color) {
            document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', params.secondary_bg_color);
        }
    }
}
