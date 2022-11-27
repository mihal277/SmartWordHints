import { Readability } from '@mozilla/readability';
import * as sanitizeHtml from 'sanitize-html';
import { OVERLAY_CONTENT_DIV_ID, OVERLAY_CONTROLS_DIV_ID, OVERLAY_DIV_ID } from './constants';

function getMaxZIndexOnSite(): number {
  return Math.max(
    ...Array.from(
      document.querySelectorAll('body *'),
      (el) => parseFloat(window.getComputedStyle(el).zIndex),
    ).filter((zIndex) => !Number.isNaN(zIndex)),
    0,
  );
}

function forceResolveOverlayCss(element: HTMLElement): void {
  window.getComputedStyle(element);
}

function extractStrippedWebsiteContent(documentClone: Document): string {
  const reader = new Readability(documentClone).parse();
  return sanitizeHtml(reader.content, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img']),
  });
}

function extractAndDisplayCleanWebsiteContent(documentClone: Document): void {
  const cleanContent = extractStrippedWebsiteContent(documentClone);
  const overlayContentDiv = document.getElementById(OVERLAY_CONTENT_DIV_ID);
  overlayContentDiv.insertAdjacentHTML('beforeend', cleanContent);
}

export function hintsOverlayIsAlreadyInjectedToDOM(): boolean {
  const element = document.getElementById(OVERLAY_DIV_ID);
  return (typeof element !== 'undefined' && element !== null);
}

export function hintsOverlayIsToggledOn(): boolean {
  return document.getElementById(OVERLAY_DIV_ID).style.height === '100%';
}

function makeSureOverlayIsOnTopOfAllWebsiteElements(): void {
  const overlay = document.getElementById(OVERLAY_DIV_ID);
  overlay.style.zIndex = (getMaxZIndexOnSite() + 1).toString();
}

export function hideOverlay(): void {
  document.getElementById(OVERLAY_CONTROLS_DIV_ID).style.height = '100%';
  document.getElementById(OVERLAY_DIV_ID).style.height = '100%';
}

export function showOverlay(): void {
  document.getElementById(OVERLAY_CONTROLS_DIV_ID).style.height = '0%';
  document.getElementById(OVERLAY_DIV_ID).style.height = '0%';
}

export function injectAndShowHintsOverlay(documentClone: Document): void {
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
