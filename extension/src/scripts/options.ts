import browser from 'webextension-polyfill';

const STATUS_LENGTH_MS: number = 1300;
const DEFAULT_API_URL: string = 'https://smartwordhints.com/api/get_hints';

function isValidUrl(str: string): boolean {
  const pattern = new RegExp('^(https?:\\/\\/)?' // protocol
      + '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|' // domain name
      + '((\\d{1,3}\\.){3}\\d{1,3}))' // OR ip (v4) address
      + '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' // port and path
      + '(\\?[;&a-z\\d%_.~+=-]*)?' // query string
      + '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
  return pattern.test(str);
}

function requestPermissions(
  permissionsToRequest: browser.Permissions.Permissions,
): void {
  function onResponse(response: boolean): void {
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

function requestPermissionsIfNeeded(url: string): void {
  if (url === DEFAULT_API_URL) return;
  requestPermissions({
    permissions: undefined,
    origins: [url],
  });
}

function saveOptions(): void {
  const serverUrlInput = document.getElementById('server-url-input') as HTMLInputElement;
  const url = serverUrlInput.value;
  if (!isValidUrl(url)) alert('Incorrect url');
  else {
    browser.storage.sync.set({ api_url: url });
    requestPermissionsIfNeeded(url);
  }
}

function restoreOptions(): void {
  const apiUrl = browser.storage.sync.get('api_url');
  apiUrl.then((res) => {
    const serverUrlInput = document.getElementById('server-url-input') as HTMLInputElement;
    serverUrlInput.value = res.api_url;
  });
}

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save-button').addEventListener('click', saveOptions);
