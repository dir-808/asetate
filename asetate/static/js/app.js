/**
 * Asetate - Main application JavaScript
 */

// API helper for making requests
const api = {
    async fetch(url, options = {}) {
        const defaults = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const response = await fetch(url, { ...defaults, ...options });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    },

    get(url) {
        return this.fetch(url);
    },

    post(url, data) {
        return this.fetch(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    patch(url, data) {
        return this.fetch(url, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    },

    delete(url) {
        return this.fetch(url, {
            method: 'DELETE',
        });
    },
};

// Toast notifications
const toast = {
    show(message, type = 'info') {
        // TODO: Implement toast notifications
        console.log(`[${type}] ${message}`);
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'error');
    },
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Asetate loaded');
});
