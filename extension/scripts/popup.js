"use strict";

var optionsLink = document.querySelector("#go-to-options");
optionsLink.addEventListener("click", function(e) {
  window.open(browser.runtime.getURL('options.html'));
})