import browser from 'webextension-polyfill';

import { DEFAULT_API_URL, EXTENSION_ICON_CLICKED_COMMAND, IS_FIREFOX } from './constants';

function setDefaultURL(): void {
  browser.storage.sync.set({ api_url: DEFAULT_API_URL });
}

function initOptions(): void {
  const apiUrl = browser.storage.sync.get('api_url');
  apiUrl.then(
    (results: any) => (!('api_url' in results) ? setDefaultURL() : {}),
  );
}
initOptions();

function startSmartWordHints(tab: browser.Tabs.Tab): void {
  browser.tabs
    .sendMessage(tab.id, { command: EXTENSION_ICON_CLICKED_COMMAND })
    .catch((error: Error) => {
      console.error(`Error starting smart word hints: ${error}`);
    });
}

if (IS_FIREFOX) browser.browserAction.onClicked.addListener(startSmartWordHints);
else browser.action.onClicked.addListener(startSmartWordHints);
