"use strict"

/*
 * This code is based on https://github.com/mozilla/readability/blob/master/Readability-readerable.js
 */

var REGEXPS = {
  unlikelyCandidates: /-ad-|ai2html|banner|breadcrumbs|combx|comment|community|cover-wrap|disqus|extra|footer|gdpr|header|legends|menu|related|remark|replies|rss|shoutbox|sidebar|skyscraper|social|sponsor|supplemental|ad-break|agegate|pagination|pager|popup|yom-remote/i,
  okMaybeItsACandidate: /and|article|body|column|content|main|shadow/i,
};

function isNodeVisible(node) {
  // Have to null-check node.style and node.className.indexOf to deal with SVG and MathML nodes.
  return (!node.style || node.style.display != "none")
    && !node.hasAttribute("hidden")
    //check for "fallback-image" so that wikimedia math images are displayed
    && (!node.hasAttribute("aria-hidden") || node.getAttribute("aria-hidden") != "true" || (node.className && node.className.indexOf && node.className.indexOf("fallback-image") !== -1));
}

function getArticleNodes(doc, options = {}) {
  if (typeof options == "function") {
    options = { visibilityChecker: options };
  }

  var defaultOptions = { minContentLength: 60, visibilityChecker: isNodeVisible };
  options = Object.assign(defaultOptions, options);

  var nodes = doc.querySelectorAll("p, pre");
  var set = new Set(nodes);

  var brNodes = doc.querySelectorAll("div > br");
  if (brNodes.length) {
    [].forEach.call(brNodes, function (node) {
      set.add(node.parentNode);
    });
  }
  nodes = Array.from(set);

  function acceptNode(node) {
    if (!options.visibilityChecker(node)) {
      return false;
    }

    var matchString = node.className + " " + node.id;
    if (REGEXPS.unlikelyCandidates.test(matchString) &&
        !REGEXPS.okMaybeItsACandidate.test(matchString)) {
      return false;
    }

    if (node.matches("li p")) {
      return false;
    }

    var textContentLength = node.textContent.trim().length;
    return textContentLength >= options.minContentLength;
  }

  return nodes.filter(acceptNode);
}