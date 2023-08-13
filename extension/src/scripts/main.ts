import browser from 'webextension-polyfill';

import {
  EXTENSION_ICON_CLICKED_COMMAND,
} from './constants';
import { Hint, parseApiResponse } from './hint';
import getOuterHTMLUpdatedWithHints from './html-manipulation';
import getArticleNodes from './get-article-nodes';

function checkHintsAreAleradyInjected(): boolean {
  // TODO
  return false;
}

function makePayloadStringFromArticleNode(articleNode: HTMLElement): string {
  const articleText = articleNode.textContent.trim();
  const payload = { text: articleText };
  return JSON.stringify(payload);
}

function getHintsFromAPI(articleNode: HTMLElement, apiUrl: string): Promise<any> {
  return fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: makePayloadStringFromArticleNode(articleNode),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status} ${response.status}`);
      }
      return response.json();
    });
}

function injectHints(hints: Hint[], articleNode: HTMLElement, difficulty: number): void {
  const updatedOuterHtml = getOuterHTMLUpdatedWithHints(hints, articleNode, difficulty);
  // TODO
  /* eslint-disable no-param-reassign */
  articleNode.innerHTML = updatedOuterHtml;
}

function handleExtensionIconClicked(): void {
  if (checkHintsAreAleradyInjected()) {
    // TODO
  } else {
    browser.storage.sync.get(['api_url', 'difficulty']).then(
      (options: Record<string, any>) => {
        const articleNodes = getArticleNodes(document);
        articleNodes.forEach((articleNode) => {
          const hintsResp = getHintsFromAPI(articleNode, options.api_url);
          hintsResp.then((responseData) => {
            const hints: Hint[] = parseApiResponse(responseData);
            injectHints(hints, articleNode, options.difficulty);
          });
          // TODO: cache hints
        });
      },
    );
  }
}

browser.runtime.onMessage.addListener((request: { command: string; }) => {
  if (request.command === EXTENSION_ICON_CLICKED_COMMAND) {
    handleExtensionIconClicked();
  } else throw Error(`Unexpected command ${request.command} received`);
});
