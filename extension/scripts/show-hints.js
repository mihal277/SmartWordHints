"use strict";

function getTextWithHints(text, hints) {
  var updatedText = ""
  var lastEnd = 0;
  for (let hint of hints) {
    updatedText += text.slice(lastEnd, hint.start_position);
    var word = text.slice(hint.start_position, hint.end_position);
    updatedText += `<ruby>${word} <rp>(</rp><rt>${hint.definition}</rt><rp>)</rp></ruby>`;
    lastEnd = hint.end_position;
    console.log(updatedText)
  }
  return updatedText;
}

var articleNodes = getArticleNodes(window.document)
articleNodes.forEach(
  node => {
    browser.runtime.sendMessage(
      {query: "get_hints", message: node.textContent.trim()}
    )
    .then(response => {
      // TODO make sure trim doesn't delete too much
      node.innerHTML = getTextWithHints(node.textContent.trim(), response.hints);
    })
    // .catch(error => node.style.border = "thick solid #ff0000");
  }
)