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
    print: '🖨',
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
 * Valid size modifiers that map to CSS classes
 */
const SIZE_MODIFIERS = ['sm', 'base', 'md', 'lg', 'xl', '2xl', '3xl', '5xl', '4xl'];

/**
 * Render an emoji icon HTML string using Noto Emoji font
 *
 * @param {string} name - Icon name (e.g., 'vinyl', 'folder')
 * @param {string} size - Size modifier ('sm', 'base', 'md', 'lg', 'xl', '2xl', '3xl', '4xl')
 *                        Default is 'xl' (24px). Uses CSS classes with design tokens.
 * @param {string|null} color - Optional color (hex or CSS color)
 * @returns {string} HTML string for the icon
 */
export function renderEmojiIcon(name, size = 'xl', color = null) {
    const char = EMOJI_CHARS[name] || EMOJI_CHARS[DEFAULT_ICON];
    const sizeClass = SIZE_MODIFIERS.includes(size) ? size : 'xl';
    const colorStyle = color ? ` style="color: ${color};"` : '';
    return `<span class="emoji-icon emoji-icon--${sizeClass}"${colorStyle}>${char}</span>`;
}

/**
 * Convert a hexcode (like "1F4BF" or "1F441-FE0F") to an emoji character
 *
 * @param {string} hexcode - Unicode hexcode(s) separated by dashes
 * @returns {string} The emoji character
 */
function hexcodeToEmoji(hexcode) {
    try {
        const codepoints = hexcode.split('-').map(cp => parseInt(cp, 16));
        return String.fromCodePoint(...codepoints);
    } catch {
        return EMOJI_CHARS[DEFAULT_ICON];
    }
}

/**
 * Check if a string looks like a hexcode (uppercase hex characters, possibly with dashes)
 *
 * @param {string} value - String to check
 * @returns {boolean} True if it looks like a hexcode
 */
function isHexcode(value) {
    return /^[0-9A-F]+(-[0-9A-F]+)*$/i.test(value);
}

/**
 * Render a crate's icon with its color
 *
 * @param {Object} crate - Crate object with icon and color_hex properties
 * @param {string} size - Size modifier ('sm', 'base', 'md', 'lg', 'xl', '2xl', '3xl', '4xl')
 *                        Default is 'xl' (24px). Uses CSS classes with design tokens.
 * @returns {string} HTML string for the crate icon
 */
export function renderCrateIcon(crate, size = 'xl') {
    const sizeClass = SIZE_MODIFIERS.includes(size) ? size : 'xl';
    const colorStyle = crate.color_hex ? ` style="color: ${crate.color_hex};"` : '';
    let char = EMOJI_CHARS[DEFAULT_ICON];

    if (crate.icon) {
        let iconValue = '';
        if (crate.icon.startsWith('emoji:')) {
            iconValue = crate.icon.slice(6);
        } else if (crate.icon.startsWith('pixel:')) {
            iconValue = crate.icon.slice(6);
        }

        if (iconValue) {
            if (isHexcode(iconValue)) {
                // New format: emoji:HEXCODE (e.g., "emoji:1F4BF")
                char = hexcodeToEmoji(iconValue);
            } else {
                // Legacy format: emoji:iconname (e.g., "emoji:vinyl")
                char = EMOJI_CHARS[iconValue] || EMOJI_CHARS[DEFAULT_ICON];
            }
        }
    }

    return `<span class="emoji-icon emoji-icon--${sizeClass}"${colorStyle}>${char}</span>`;
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
        btn.innerHTML = renderEmojiIcon(icon.name, 'xl');
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
    // Map legacy scale to size class (scale 1.5 ≈ 18px → 'md')
    const sizeMap = { 1: 'sm', 1.25: 'base', 1.5: 'md', 2: 'xl', 2.5: '2xl', 3: '3xl' };
    const size = sizeMap[scale] || 'md';
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
        SIZE_MODIFIERS,
        renderEmojiIcon,
        renderCrateIcon,
        renderEmojiIconGrid,
        renderPixelIconGrid,
        renderPixelIcon,
        getIconName,
        formatIconForStorage,
        hexcodeToEmoji,
        isHexcode,
    };
}

// Export helper functions for direct use
export { hexcodeToEmoji, isHexcode };
