const form = document.getElementById('chat-form');
const input = document.getElementById('query-input');
const chatWindow = document.getElementById('chat-window');
const sourcesContainer = document.getElementById('sources-container');
const sidebarToggle = document.getElementById('toggle-sidebar');
const sidebar = document.querySelector('.sidebar');

// Auto-expand textarea
input.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if(this.value === '') this.style.height = 'auto';
});

// Mobile Sidebar Toggle
if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
}

// Handle Submit
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    // Add User Message
    addMessage(query, 'user');
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query, top_k: 4 })
        });

        if (!response.ok) {
            throw new Error('Backend returned an error.');
        }

        const data = await response.json();
        
        // Remove typing indicator
        document.getElementById(typingId).remove();
        
        // Populate specific message elements
        addAIMessage(data.answer, data.thought);
        
        // Update Sidebar Sources
        updateSources(data.retrieved_context);

    } catch (error) {
        document.getElementById(typingId).remove();
        addMessage(`Connection Error: Make sure your FastAPI backend is running! Details: ${error.message}`, 'ai');
    }
});

// Allow Enter to submit, Shift+Enter for newline
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        form.dispatchEvent(new Event('submit'));
    }
});

function addMessage(text, role) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;
    
    // Convert basic markdown formatting like bold text or newlines
    let formattedText = text.replace(/\n/g, '<br/>');
    formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    const icon = role === 'user' ? 'user' : 'cpu';
    
    msgDiv.innerHTML = `
        <div class="avatar"><i data-feather="${icon}"></i></div>
        <div class="message-content">${formattedText}</div>
    `;
    
    chatWindow.appendChild(msgDiv);
    feather.replace();
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addAIMessage(answer, thought) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ai-message`;
    
    let contentHtml = '';
    
    // If the model produced <think> tags, format it beautifully.
    if (thought && thought.trim().length > 0) {
        let cleanThought = thought.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, '<br/>');
        contentHtml += `
            <div class="thought-block" onclick="this.classList.toggle('expanded')">
                <span>&#9881; View AI Thought Process... (Click to expand)</span>
                <div class="thought-content">${cleanThought}</div>
            </div>
        `;
    }
    
    let formattedAnswer = answer.replace(/\n/g, '<br/>');
    // Highlight citations e.g. Source [1] (Page 22)
    formattedAnswer = formattedAnswer.replace(/(Source \[\d+\] \(Page \d+\))/g, '<strong style="color: var(--accent-color)">$1</strong>');
    formattedAnswer = formattedAnswer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    contentHtml += `<div>${formattedAnswer}</div>`;

    msgDiv.innerHTML = `
        <div class="avatar"><i data-feather="cpu"></i></div>
        <div class="message-content">${contentHtml}</div>
    `;
    
    chatWindow.appendChild(msgDiv);
    feather.replace();
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ai-message`;
    msgDiv.id = id;
    
    msgDiv.innerHTML = `
        <div class="avatar"><i data-feather="cpu"></i></div>
        <div class="message-content pb-0">
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    
    chatWindow.appendChild(msgDiv);
    feather.replace();
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return id;
}

function updateSources(sources) {
    if (!sources || sources.length === 0) {
        sourcesContainer.innerHTML = `<div class="empty-state"><p>No relevant sources found for this query.</p></div>`;
        return;
    }

    let html = '';
    sources.forEach((src, index) => {
        // Truncate context for display
        let contextMatch = src.content.match(/Context: \[(.*?)\]/);
        let tags = contextMatch ? contextMatch[1] : 'Legal Document';
        let textContent = src.content.split('-- Text:')[1] || src.content;
        
        html += `
            <div class="source-card">
                <div class="source-header">
                    <span>Source [${index + 1}]</span>
                    <span class="source-badge">Pg ${src.page}</span>
                </div>
                <!-- <div style="font-size: 0.75rem; color: #a0a0b0; margin-bottom: 6px;">${tags}</div> -->
                <div class="source-text">${textContent.trim()}</div>
            </div>
        `;
    });
    
    sourcesContainer.innerHTML = html;
}
