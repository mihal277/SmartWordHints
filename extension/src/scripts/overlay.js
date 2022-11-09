import { Readability } from '@mozilla/readability';
import sanitizeHtml from 'sanitize-html';
import { OVERLAY_CONTENT_DIV_ID, OVERLAY_CONTROLS_DIV_ID, OVERLAY_DIV_ID } from './constants';

function getMaxZIndexOnSite() {
  return Math.max(
    ...Array.from(
      document.querySelectorAll('body *'),
      (el) => parseFloat(window.getComputedStyle(el).zIndex),
    ).filter((zIndex) => !Number.isNaN(zIndex)),
    0,
  );
}

function forceResolveOverlayCss(element) {
  window.getComputedStyle(element);
}

function extractStrippedWebsiteContent(documentClone) {
  const reader = new Readability(documentClone).parse();
  return sanitizeHtml(reader.content, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img']),
  });
}

function extractAndDisplayCleanWebsiteContent(documentClone) {
  const cleanContent = extractStrippedWebsiteContent(documentClone);
  const overlayContentDiv = document.getElementById(OVERLAY_CONTENT_DIV_ID);
  overlayContentDiv.insertAdjacentHTML('beforeend', cleanContent);
}

export function hintsOverlayIsAlreadyInjectedToDOM() {
  const element = document.getElementById(OVERLAY_DIV_ID);
  return (typeof element !== 'undefined' && element !== null);
}

export function hintsOverlayIsToggledOn() {
  return document.getElementById(OVERLAY_DIV_ID).style.height === '100%';
}

function makeSureOverlayIsOnTopOfAllWebsiteElements() {
  const overlay = document.getElementById(OVERLAY_DIV_ID);
  overlay.style.zIndex = (getMaxZIndexOnSite() + 1).toString();
}

export function hideOverlay() {
  document.getElementById(OVERLAY_CONTROLS_DIV_ID).style.height = '100%';
  document.getElementById(OVERLAY_DIV_ID).style.height = '100%';
}

export function showOverlay() {
  document.getElementById(OVERLAY_CONTROLS_DIV_ID).style.height = '0%';
  document.getElementById(OVERLAY_DIV_ID).style.height = '0%';
}

export function injectAndShowHintsOverlay(documentClone) {
  fetch(browser.runtime.getURL('/overlay.html'))
    .then((r) => r.text())
    .then((html) => {
      document.body.insertAdjacentHTML('beforeend', html);
      const overlay = document.getElementById(OVERLAY_DIV_ID);
      forceResolveOverlayCss(overlay);
      extractAndDisplayCleanWebsiteContent(documentClone);
      makeSureOverlayIsOnTopOfAllWebsiteElements();
      hideOverlay();
    });
}
