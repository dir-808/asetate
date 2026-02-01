/**
 * Centralized Icon System (Noto Emoji Font)
 * =========================================
 * All icon data and rendering logic in one place.
 * Import this module in any script that needs icons.
 *
 * Usage:
 *     import { EMOJI_CHARS, renderEmojiIcon, renderCrateIcon, renderEmojiIconGrid } from '/static/js/icons.js';
 *
 *     renderEmojiIcon('vinyl', 24);
 *     renderCrateIcon(crate, 32);
 *     renderEmojiIconGrid(container, onSelectCallback, 'vinyl');
 */

/**
 * Emoji character mapping
 * Maps friendly icon names to Unicode emoji characters
 * Using Noto Emoji font (monochrome, medium weight)
 */
export const EMOJI_CHARS = {
    folder: '📁',
    vinyl: '💿',
    headphones: '🎧',
    music: '🎵',
    speaker: '🔊',
    disco: '🪩',
    wave: '🌊',
    fire: '🔥',
    bolt: '⚡',
    star: '⭐',
    heart: '❤',
    diamond: '💎',
    crown: '👑',
    sun: '🌞',
    moon: '🌙',
    globe: '🌍',
    clock: '🕰',
    skull: '💀',
    box: '📦',
    check: '✔',
    plus: '➕',
    link: '🔗',
    edit: '✏',
    sync: '🔄',
    notes: '📝',
    tag: '🏷',
};

/** Legacy alias for backwards compatibility */
export const EMOJI_CODES = EMOJI_CHARS;

/**
 * Available emoji icons for crates
 * This is the single source of truth for icon options
 */
export const EMOJI_ICONS = [
    { name: 'folder', label: 'Folder' },
    { name: 'vinyl', label: 'Vinyl' },
    { name: 'headphones', label: 'Headphones' },
    { name: 'music', label: 'Music' },
    { name: 'speaker', label: 'Speaker' },
    { name: 'disco', label: 'Disco' },
    { name: 'wave', label: 'Wave' },
    { name: 'fire', label: 'Fire' },
    { name: 'bolt', label: 'Bolt' },
    { name: 'star', label: 'Star' },
    { name: 'heart', label: 'Heart' },
    { name: 'diamond', label: 'Diamond' },
    { name: 'crown', label: 'Crown' },
    { name: 'sun', label: 'Sun' },
    { name: 'moon', label: 'Moon' },
    { name: 'globe', label: 'Globe' },
    { name: 'clock', label: 'Clock' },
    { name: 'skull', label: 'Skull' },
    { name: 'box', label: 'Box' },
    { name: 'check', label: 'Check' },
    { name: 'plus', label: 'Plus' },
];

/** Legacy alias */
export const PIXEL_ICONS = EMOJI_ICONS;

/** Default icon when none is specified */
export const DEFAULT_ICON = 'folder';

/**
 * Render an emoji icon HTML string using Noto Emoji font
 *
 * @param {string} name - Icon name (e.g., 'vinyl', 'folder')
 * @param {number} size - Font size in pixels (default 24)
 * @param {string|null} color - Optional color (hex or CSS color)
 * @returns {string} HTML string for the icon
 */
export function renderEmojiIcon(name, size = 24, color = null) {
    const char = EMOJI_CHARS[name] || EMOJI_CHARS[DEFAULT_ICON];
    const colorStyle = color ? ` color: ${color};` : '';
    return `<span class="emoji-icon" style="font-size: ${size}px;${colorStyle}">${char}</span>`;
}

/**
 * Render a crate's icon with its color
 *
 * @param {Object} crate - Crate object with icon and color_hex properties
 * @param {number} size - Font size in pixels (default 24)
 * @returns {string} HTML string for the crate icon
 */
export function renderCrateIcon(crate, size = 24) {
    const colorStyle = crate.color_hex ? ` color: ${crate.color_hex};` : '';
    let iconName = DEFAULT_ICON;
    // Support both 'emoji:name' and legacy 'pixel:name' formats
    if (crate.icon) {
        if (crate.icon.startsWith('emoji:')) {
            iconName = crate.icon.slice(6);
        } else if (crate.icon.startsWith('pixel:')) {
            iconName = crate.icon.slice(6);
        }
    }
    const char = EMOJI_CHARS[iconName] || EMOJI_CHARS[DEFAULT_ICON];
    return `<span class="emoji-icon" style="font-size: ${size}px;${colorStyle}">${char}</span>`;
}

/**
 * Render an emoji icon grid for icon selection
 *
 * @param {HTMLElement} container - Container element to render grid into
 * @param {Function} onSelect - Callback when icon is selected (receives icon name)
 * @param {string|null} selectedIcon - Currently selected icon name (for highlighting)
 */
export function renderEmojiIconGrid(container, onSelect, selectedIcon = null) {
    container.innerHTML = '';
    EMOJI_ICONS.forEach(icon => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'emoji-icon-grid-item' + (selectedIcon === icon.name ? ' selected' : '');
        btn.dataset.icon = icon.name;
        btn.title = icon.label;
        btn.innerHTML = renderEmojiIcon(icon.name, 24);
        btn.addEventListener('click', () => onSelect(icon.name));
        container.appendChild(btn);
    });
}

/** Legacy alias for grid rendering */
export const renderPixelIconGrid = renderEmojiIconGrid;

/**
 * Get icon name from a crate's icon field
 * Handles both "emoji:iconname" and legacy "pixel:iconname" formats
 *
 * @param {string|null} iconField - The crate.icon field value
 * @returns {string} The icon name (or default)
 */
export function getIconName(iconField) {
    if (iconField) {
        if (iconField.startsWith('emoji:')) {
            return iconField.slice(6);
        }
        if (iconField.startsWith('pixel:')) {
            return iconField.slice(6);
        }
    }
    return DEFAULT_ICON;
}

/**
 * Format icon name for storage in database
 *
 * @param {string} iconName - Plain icon name (e.g., 'vinyl')
 * @returns {string} Formatted for storage (e.g., 'emoji:vinyl')
 */
export function formatIconForStorage(iconName) {
    return `emoji:${iconName}`;
}

/**
 * Legacy: Render a CSS pixel art icon
 * @deprecated Use renderEmojiIcon instead
 */
export function renderPixelIcon(name, scale = 1.5, color = null) {
    // Redirect to emoji icon with size approximation
    const size = Math.round(12 * scale);
    return renderEmojiIcon(name, size, color);
}

// Also expose on window for AJAX-loaded partials that can't use ES6 imports
if (typeof window !== 'undefined') {
    window.AsetateIcons = {
        EMOJI_ICONS,
        EMOJI_CHARS,
        EMOJI_CODES: EMOJI_CHARS,
        PIXEL_ICONS,
        DEFAULT_ICON,
        renderEmojiIcon,
        renderCrateIcon,
        renderEmojiIconGrid,
        renderPixelIconGrid,
        renderPixelIcon,
        getIconName,
        formatIconForStorage,
    };
}
