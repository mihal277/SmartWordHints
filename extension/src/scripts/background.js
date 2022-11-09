import { DEFAULT_API_URL, EXTENSION_ICON_CLICKED_COMMAND } from './constants';

function setDefaultURL() {
  browser.storage.sync.set({ api_url: DEFAULT_API_URL });
}

function initOptions() {
  const apiUrl = browser.storage.sync.get('api_url');
  apiUrl.then(
    (results) => (!('api_url' in results) ? setDefaultURL() : {}),
  );
}
initOptions();

// function handleMessage(request, sender, sendResponse) {
//   if (request.query === 'get_hints') {
//     const payload = { text: request.messsage, options: { difficulty: 2000 } };
//     const url = browser.storage.sync.get('api_url');
//     url.then((res) => {
//       fetch(res.api_url, {
//         method: 'POST',
//         body: JSON.stringify(payload),
//         headers: {
//           'Content-Type': 'application/json',
//         },
//       })
//         .then((response) => response.json())
//         .then((json) => sendResponse(json));
//       // .catch(error => ...)
//     });
//     return true;
//   }
//   return false;
// }
//
// browser.runtime.onMessage.addListener(handleMessage);

function startSmartWordHints(tab) {
  browser.tabs.sendMessage(tab.id, { command: EXTENSION_ICON_CLICKED_COMMAND }).catch((error) => {
    console.error(`Error starting smart word hints: ${error}`);
  });
}

browser.browserAction.onClicked.addListener(startSmartWordHints);
