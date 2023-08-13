export const EXTENSION_ICON_CLICKED_COMMAND: string = 'extension-icon-clicked';

export const DEFAULT_API_URL: string = 'http://localhost:8081/api/v1/get_hints';
export const DEFAULT_DIFFICULTY: number = 3000;

export const IS_EDGE = navigator.userAgent.indexOf('Edg') >= 0;
export const IS_FIREFOX = navigator.userAgent.indexOf('Firefox') >= 0;
export const IS_CHROME = IS_EDGE === false && IS_FIREFOX === false;
