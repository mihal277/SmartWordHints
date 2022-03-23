/**
 * @jest-environment jsdom
 */

import getArticleNodes from '../scripts/article-extraction/simple/get-article-nodes';

describe('Test function getArticleNodes on simple examples', () => {
  test('trivial example', () => {
    const simpleArticle = `<p>${'Simple article. '.repeat(30)}</p>`;
    document.body.innerHTML = simpleArticle;
    const result = getArticleNodes(document.body, {});
    expect(result.map((node) => node.outerHTML)).toStrictEqual([simpleArticle]);
  });
});
