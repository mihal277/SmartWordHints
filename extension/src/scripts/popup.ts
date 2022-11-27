const optionsLink = document.querySelector('#go-to-options');

optionsLink.addEventListener('click', () => {
  window.open(browser.runtime.getURL('options.html'));
});
