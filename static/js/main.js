document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle');
    if(themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            document.documentElement.classList.toggle('light-theme');
        });
    }

    // Radial Glow Spotlight Overlay tracking cursor (Theme A)
    const cards = document.querySelectorAll('.card');
    document.addEventListener('mousemove', (e) => {
        // Only apply if we are NOT in light theme
        if (!document.documentElement.classList.contains('light-theme')) {
            cards.forEach(card => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--mouse-x', `${x}px`);
                card.style.setProperty('--mouse-y', `${y}px`);
            });
        }
    });
});

// Example function to interact with the Mock Interview Gemini Endpoint
async function sendInterviewMessage(message, historyStr) {
    try {
        const response = await fetch('/api/mock_interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, history: historyStr })
        });
        const data = await response.json();
        return data.reply;
    } catch (error) {
        console.error("Failed to fetch AI response:", error);
    }
}
