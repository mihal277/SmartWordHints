"use strict";

function getTextWithHints(text, hints) {
  var updatedText = ""
  var lastEnd = 0;
  for (let hint of hints) {
    updatedText += text.slice(lastEnd, hint.start);
    var word = text.slice(hint.start, hint.end);
    updatedText += `<ruby>${word} <rp>(</rp><rt>${hint.definition}</rt><rp>)</rp></ruby>`;
    lastEnd = hint.end;
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
      node.style.border = "thick solid #66ff99";
      // TODO make sure trim doesn't delete too much
      var withHints = getTextWithHints(node.textContent.trim(), response.hints);

      var paragraph = document.createElement('div');
      paragraph.innerHTML = withHints;

      node.replaceWith(paragraph);
      console.log(response);
    })
    .catch(error => node.style.border = "thick solid #ff0000");
  }
)