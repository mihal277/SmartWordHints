import browser from 'webextension-polyfill';

import { isProbablyReaderable } from '@mozilla/readability';

import {
  CLOSE_OVERLAY_EVENT_NAME,
  EXTENSION_ICON_CLICKED_COMMAND,
} from './constants';
import {
  hintsOverlayIsAlreadyInjectedToDOM,
  hintsOverlayIsToggledOn,
  injectAndShowHintsOverlay,
  showOverlay,
  hideOverlay,
} from './overlay';

function handleExtensionIconClickedWhenOverlayIsAlreadyInjected(): void {
  if (hintsOverlayIsToggledOn()) {
    showOverlay();
  } else {
    hideOverlay();
  }
}

function handleExtensionIconClicked(): void {
  if (hintsOverlayIsAlreadyInjectedToDOM()) {
    handleExtensionIconClickedWhenOverlayIsAlreadyInjected();
  } else {
    const documentClone = document.cloneNode(true) as Document;
    if (isProbablyReaderable(documentClone)) {
      injectAndShowHintsOverlay(documentClone);
    }
  }
}

browser.runtime.onMessage.addListener((request: { command: string; }) => {
  if (request.command === EXTENSION_ICON_CLICKED_COMMAND) {
    handleExtensionIconClicked();
  } else throw Error(`Unexpected command ${request.command} received`);
});

document.addEventListener(CLOSE_OVERLAY_EVENT_NAME, () => {
  showOverlay();
});
