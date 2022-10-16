const optionsLink = document.querySelector('#go-to-options');
// eslint-disable-next-line no-unused-vars
optionsLink.addEventListener('click', (e) => {
  window.open(browser.runtime.getURL('options.html'));
});
