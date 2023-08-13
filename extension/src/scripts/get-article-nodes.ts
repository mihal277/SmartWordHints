/*
 * This code is based on https://github.com/mozilla/readability/blob/main/Readability-readerable.js
 */

const REGEXPS = {
  unlikelyCandidates: /-ad-|ai2html|banner|breadcrumbs|combx|comment|community|cover-wrap|disqus|extra|footer|gdpr|header|legends|menu|related|remark|replies|rss|shoutbox|sidebar|skyscraper|social|sponsor|supplemental|ad-break|agegate|pagination|pager|popup|yom-remote/i,
  okMaybeItsACandidate: /and|article|body|column|content|main|shadow/i,
};

function isNodeVisible(node: HTMLElement) {
  // Have to null-check node.style and node.className.indexOf to deal with SVG and MathML nodes.
  return (!node.style || node.style.display !== 'none')
    && !node.hasAttribute('hidden')
    // check for "fallback-image" so that wikimedia math images are displayed
    && (!node.hasAttribute('aria-hidden') || node.getAttribute('aria-hidden') !== 'true' || (node.className && node.className.indexOf && node.className.indexOf('fallback-image') !== -1));
}

export default function getArticleNodes(doc: Document): HTMLElement[] {
  const minContentLength = 60;

  const nodes = doc.querySelectorAll('p, pre') as NodeListOf<HTMLElement>;
  const nodesSet = new Set(nodes);

  const brNodes = doc.querySelectorAll('div > br') as NodeListOf<HTMLElement>;
  if (brNodes.length) {
    [].forEach.call(brNodes, (node: HTMLElement) => {
      nodesSet.add(node.parentElement);
    });
  }
  const nodesArr = Array.from(nodesSet);

  function acceptNode(node: HTMLElement) {
    if (!isNodeVisible(node)) {
      return false;
    }

    const matchString = `${node.className} ${node.id}`;
    if (REGEXPS.unlikelyCandidates.test(matchString)
        && !REGEXPS.okMaybeItsACandidate.test(matchString)) {
      return false;
    }

    if (node.matches('li p')) {
      return false;
    }

    const textContentLength = node.textContent.trim().length;
    return textContentLength >= minContentLength;
  }

  return nodesArr.filter(acceptNode);
}