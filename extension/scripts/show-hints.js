function getTextWithHints(text, hints) {
  let updatedText = '';
  let lastEnd = 0;
  // eslint-disable-next-line no-restricted-syntax
  for (const hint of hints) {
    updatedText += text.slice(lastEnd, hint.start_position);
    const word = text.slice(hint.start_position, hint.end_position);
    updatedText += `<ruby>${word} <rp>(</rp><rt>${hint.definition}</rt><rp>)</rp></ruby>`;
    lastEnd = hint.end_position;
  }
  return updatedText;
}

// eslint-disable-next-line no-undef
const articleNodes = getArticleNodes(window.document);
articleNodes.forEach(
  (node) => {
    browser.runtime.sendMessage(
      { query: 'get_hints', message: node.textContent.trim() },
    )
      .then((response) => {
      // TODO make sure trim doesn't delete too much
        // eslint-disable-next-line no-param-reassign
        node.innerHTML = getTextWithHints(node.textContent.trim(), response.hints);
      });
    // .catch(error => node.style.border = "thick solid #ff0000");
  },
);
