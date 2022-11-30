export const EXTENSION_ICON_CLICKED_COMMAND: string = 'extension-icon-clicked';

export const OVERLAY_DIV_ID: string = 'smart-word-hints-overlay';
export const OVERLAY_CONTENT_DIV_ID: string = 'smart-word-hints-overlay-content';
export const OVERLAY_CONTROLS_DIV_ID: string = 'smart-word-hints-overlay-controls';

export const CLOSE_OVERLAY_EVENT_NAME: string = 'closeSmartWordHintsOverlay';

export const DEFAULT_API_URL: string = 'http://localhost/api/get_hints';

export const IS_EDGE = navigator.userAgent.indexOf('Edg') >= 0;
export const IS_FIREFOX = navigator.userAgent.indexOf('Firefox') >= 0;
export const IS_CHROME = IS_EDGE === false && IS_FIREFOX === false;
