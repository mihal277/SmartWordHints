import browser from 'webextension-polyfill';

import {
  DEFAULT_API_URL, DEFAULT_DIFFICULTY, EXTENSION_ICON_CLICKED_COMMAND, IS_FIREFOX,
} from './constants';

function initOptions(): void {
  browser.storage.sync.get(['api_url', 'difficulty']).then(
    (options: Record<string, any>) => {
      const apiUrl = options.api_url || DEFAULT_API_URL;
      const difficulty = options.difficulty || DEFAULT_DIFFICULTY;
      browser.storage.sync.set({ api_url: apiUrl, difficulty });
    },
  );
}
initOptions();

function startSmartWordHints(tab: browser.Tabs.Tab): void {
  browser.tabs
    .sendMessage(tab.id, { command: EXTENSION_ICON_CLICKED_COMMAND })
    .catch((error: Error) => {
      /* eslint-disable no-console */
      console.error(`Error starting smart word hints: ${error}`);
    });
}

if (IS_FIREFOX) browser.browserAction.onClicked.addListener(startSmartWordHints);
else browser.action.onClicked.addListener(startSmartWordHints);
