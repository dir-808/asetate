/**
 * Centralized Icon System
 * =======================
 * All icon data and rendering logic in one place.
 * Import this module in any script that needs icons.
 *
 * Usage:
 *     import { PIXEL_ICONS, renderPixelIcon, renderCrateIcon, renderPixelIconGrid } from '/static/js/icons.js';
 *
 *     renderPixelIcon('vinyl', 2);
 *     renderCrateIcon(crate, 1.5);
 *     renderPixelIconGrid(container, onSelectCallback, 'vinyl');
 */

/**
 * Available pixel icons for crates
 * This is the single source of truth for icon options
 */
export const PIXEL_ICONS = [
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

/** Default icon when none is specified */
export const DEFAULT_ICON = 'folder';

/**
 * Render a pixel icon HTML string
 *
 * @param {string} name - Icon name (e.g., 'vinyl', 'folder')
 * @param {number} scale - Size multiplier (default 1.5)
 * @param {string|null} color - Optional color (hex or CSS color)
 * @returns {string} HTML string for the icon
 */
export function renderPixelIcon(name, scale = 1.5, color = null) {
    const colorStyle = color ? ` color: ${color};` : '';
    return `<span class="px-icon px-icon--${name}" style="--px-scale: ${scale};${colorStyle}"></span>`;
}

/**
 * Render a crate's icon with its color
 *
 * @param {Object} crate - Crate object with icon and color_hex properties
 * @param {number} scale - Size multiplier (default 1.2)
 * @returns {string} HTML string for the crate icon
 */
export function renderCrateIcon(crate, scale = 1.2) {
    const colorStyle = crate.color_hex ? ` color: ${crate.color_hex};` : '';
    let iconName = DEFAULT_ICON;
    if (crate.icon && crate.icon.startsWith('pixel:')) {
        iconName = crate.icon.slice(6);
    }
    return `<span class="px-icon px-icon--${iconName}" style="--px-scale: ${scale};${colorStyle}"></span>`;
}

/**
 * Render a pixel icon grid for icon selection
 *
 * @param {HTMLElement} container - Container element to render grid into
 * @param {Function} onSelect - Callback when icon is selected (receives icon name)
 * @param {string|null} selectedIcon - Currently selected icon name (for highlighting)
 */
export function renderPixelIconGrid(container, onSelect, selectedIcon = null) {
    container.innerHTML = '';
    PIXEL_ICONS.forEach(icon => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'pixel-icon-grid-item' + (selectedIcon === icon.name ? ' selected' : '');
        btn.dataset.icon = icon.name;
        btn.title = icon.label;
        btn.innerHTML = renderPixelIcon(icon.name, 1.5);
        btn.addEventListener('click', () => onSelect(icon.name));
        container.appendChild(btn);
    });
}

/**
 * Get icon name from a crate's icon field
 * Handles the "pixel:iconname" format
 *
 * @param {string|null} iconField - The crate.icon field value
 * @returns {string} The icon name (or default)
 */
export function getIconName(iconField) {
    if (iconField && iconField.startsWith('pixel:')) {
        return iconField.slice(6);
    }
    return DEFAULT_ICON;
}

/**
 * Format icon name for storage in database
 *
 * @param {string} iconName - Plain icon name (e.g., 'vinyl')
 * @returns {string} Formatted for storage (e.g., 'pixel:vinyl')
 */
export function formatIconForStorage(iconName) {
    return `pixel:${iconName}`;
}

// Also expose on window for AJAX-loaded partials that can't use ES6 imports
if (typeof window !== 'undefined') {
    window.AsetateIcons = {
        PIXEL_ICONS,
        DEFAULT_ICON,
        renderPixelIcon,
        renderCrateIcon,
        renderPixelIconGrid,
        getIconName,
        formatIconForStorage,
    };
}
