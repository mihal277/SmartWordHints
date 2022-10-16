const STATUS_LENGTH_MS = 1300;
const DEFAULT_API_URL = 'https://smartwordhints.com/api/get_hints';

function isValidUrl(str) {
  const pattern = new RegExp('^(https?:\\/\\/)?' // protocol
      + '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|' // domain name
      + '((\\d{1,3}\\.){3}\\d{1,3}))' // OR ip (v4) address
      + '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' // port and path
      + '(\\?[;&a-z\\d%_.~+=-]*)?' // query string
      + '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
  return pattern.test(str);
}

function requestPermissions(permissionsToRequest) {
  function onResponse(response) {
    const status = document.getElementById('status');
    if (response) {
      status.textContent = 'Options saved.';
    } else {
      status.textContent = 'Permissions refused.';
    }
    setTimeout(() => {
      status.textContent = '';
    }, STATUS_LENGTH_MS);
  }

  browser.permissions.request(permissionsToRequest).then(onResponse);
}

function requestPermissionsIfNeeded(url) {
  if (url === DEFAULT_API_URL) return;
  const permissionsToRequest = {
    permissions: null,
    origins: [url],
  };
  requestPermissions(permissionsToRequest);
}

function saveOptions() {
  const url = document.getElementById('server-url-input').value;
  if (!isValidUrl(url)) alert('Incorrect url');
  else {
    browser.storage.sync.set({ api_url: url });
    requestPermissionsIfNeeded(url);
  }
}

function restoreOptions() {
  const apiUrl = browser.storage.sync.get('api_url');
  apiUrl.then((res) => {
    document.getElementById('server-url-input').value = res.api_url;
  });
}

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save-button').addEventListener('click', saveOptions);
