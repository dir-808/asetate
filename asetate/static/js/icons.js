/**
 * Centralized Icon System
 * =======================
 * All icon data and rendering logic in one place.
 * Import this module in any script that needs icons.
 *
 * Usage:
 *     import { EMOJI_ICONS, renderEmojiIcon, renderCrateIcon, renderEmojiIconGrid } from '/static/js/icons.js';
 *
 *     renderEmojiIcon('vinyl', 24);
 *     renderCrateIcon(crate, 32);
 *     renderEmojiIconGrid(container, onSelectCallback, 'vinyl');
 */

/**
 * Emoji code mapping - OpenMoji SVG filenames
 * Maps friendly icon names to OpenMoji unicode points
 */
export const EMOJI_CODES = {
    folder: '1F4C1',
    vinyl: '1F4BF',
    headphones: '1F3A7',
    music: '1F3B5',
    speaker: '1F50A',
    disco: '1FAA9',
    wave: '1F30A',
    fire: '1F525',
    bolt: '26A1',
    star: '2B50',
    heart: '2764',
    diamond: '1F48E',
    crown: '1F451',
    sun: '1F31E',
    moon: '1F319',
    globe: '1F30D',
    clock: '1F570',
    skull: '1F480',
    box: '1F4E6',
    check: '2714',
    plus: '2795',
    link: '1F517',
    edit: '270F',
    sync: '1F504',
    notes: '1F4DD',
    tag: '1F3F7',
};

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
 * Get filter size class based on icon size
 * @param {number} size - Size in pixels
 * @returns {string} Filter size class (sm, md, lg)
 */
function getFilterSize(size) {
    if (size <= 20) return 'sm';
    if (size >= 36) return 'lg';
    return 'md';
}

/**
 * Render an emoji icon HTML string (OpenMoji SVG with pixel art filter)
 *
 * @param {string} name - Icon name (e.g., 'vinyl', 'folder')
 * @param {number} size - Size in pixels (default 24)
 * @param {string|null} color - Optional color (hex or CSS color)
 * @returns {string} HTML string for the icon
 */
export function renderEmojiIcon(name, size = 24, color = null) {
    const code = EMOJI_CODES[name] || EMOJI_CODES[DEFAULT_ICON];
    const filterSize = getFilterSize(size);
    const colorStyle = color ? ` color: ${color};` : '';
    return `<span class="emoji-icon emoji-icon--${filterSize}" style="width: ${size}px; height: ${size}px;${colorStyle} -webkit-mask-image: url('/static/emoji/${code}.svg'); mask-image: url('/static/emoji/${code}.svg');"></span>`;
}

/**
 * Render a crate's icon with its color (emoji version)
 *
 * @param {Object} crate - Crate object with icon and color_hex properties
 * @param {number} size - Size in pixels (default 24)
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
    const code = EMOJI_CODES[iconName] || EMOJI_CODES[DEFAULT_ICON];
    const filterSize = getFilterSize(size);
    return `<span class="emoji-icon emoji-icon--${filterSize}" style="width: ${size}px; height: ${size}px;${colorStyle} -webkit-mask-image: url('/static/emoji/${code}.svg'); mask-image: url('/static/emoji/${code}.svg');"></span>`;
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
    const colorStyle = color ? ` color: ${color};` : '';
    return `<span class="px-icon px-icon--${name}" style="--px-scale: ${scale};${colorStyle}"></span>`;
}

// Also expose on window for AJAX-loaded partials that can't use ES6 imports
if (typeof window !== 'undefined') {
    window.AsetateIcons = {
        EMOJI_ICONS,
        EMOJI_CODES,
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
