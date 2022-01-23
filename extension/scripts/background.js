const DEFAULT_API_URL = 'http://localhost/api/get_hints';

function setDefaultURL() {
  browser.storage.sync.set({ api_url: DEFAULT_API_URL });
}

function initOptions() {
  const apiUrl = browser.storage.sync.get('api_url');
  apiUrl.then(
    (results) => (!('api_url' in results) ? setDefaultURL() : {}),
  );
}

function handleMessage(request, sender, sendResponse) {
  if (request.query === 'get_hints') {
    const payload = { text: request.messsage, options: { difficulty: 2000 } };
    const url = browser.storage.sync.get('api_url');
    url.then((res) => {
      fetch(res.api_url, {
        method: 'POST',
        body: JSON.stringify(payload),
        headers: {
          'Content-Type': 'application/json',
        },
      })
        .then((response) => response.json())
        .then((json) => sendResponse(json));
      // .catch(error => ...)
    });
    return true;
  }
  return false;
}

initOptions();
browser.runtime.onMessage.addListener(handleMessage);
