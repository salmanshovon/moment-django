// static/js/messages.js
function showMessage(message, type = 'info') {
    let messageContainer = document.getElementById('message-container');

    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        messageContainer.className = 'floating-messages-container';
        document.body.appendChild(messageContainer);
    }

    const messageBox = document.createElement('div');
    messageBox.className = `floating-message ${type}`; // Add type for styling
    messageBox.innerHTML = `
        <p>${message}</p>
        <button class="close-btn" onclick="hideSingleMessage(this.parentElement)">×</button>
    `;

    messageContainer.appendChild(messageBox);

    // Auto-hide after 5 seconds
    setTimeout(() => hideSingleMessage(messageBox), 5000);
}

function hideSingleMessage(messageBox) {
    if (messageBox) {
        messageBox.classList.add('fade-out');
        setTimeout(() => messageBox.remove(), 400); // Remove element after fade
    }
}