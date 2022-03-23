import { JSDOM } from 'jsdom';
import { exportedForTesting } from '../scripts/article-extraction/advanced/get-article-nodes';

const { getLang, getWordStats, getLinksDensity } = exportedForTesting;

describe('Test function getLang', () => {
  test('doc with lang as html lang attribute', () => {
    const dom = new JSDOM('<html lang="en"></html>');
    expect(getLang(dom.window.document)).toStrictEqual('en');
  });

  test('doc without lang', () => {
    const dom = new JSDOM('<html><body></body></html>');
    expect(getLang(dom.window.document)).toStrictEqual(null);
  });
});

describe('Test function getWordStats', () => {
  test('simple english sentence with unnecessary commas', () => {
    const content = 'I went to the doctor, and, received, a drug.';
    expect(getWordStats(content, 'en')).toStrictEqual({
      wordCount: 9,
      stopwordCount: 4,
      stopWords: ['went', 'to', 'the', 'and'],
    });
  });
});

describe('Test function getLinksDensity', () => {
  test('node with no links', () => {
    const dom = new JSDOM('<html lang="en"><body><p id="p">Simple text in English.</p></body></html>');
    const node = dom.window.document.getElementById('p');
    expect(getLinksDensity(node)).toEqual(0.0);
  });

  test('node with one link with single word', () => {
    const dom = new JSDOM(
      '<html lang="en"><body><p id="p">Simple <a href="https://link.com/">text</a> in English.</p></body></html>',
    );
    const node = dom.window.document.getElementById('p');
    expect(getLinksDensity(node)).toEqual(0.25);
  });

  test('node with one link with two words', () => {
    const dom = new JSDOM(
      '<html lang="en"><body><p id="p">Simple <a href="https://link.com/">text in English.</a></p></body></html>',
    );
    const node = dom.window.document.getElementById('p');
    expect(getLinksDensity(node)).toEqual(0.75);
  });

  test('node with one long link', () => {
    const dom = new JSDOM(
      '<html lang="en"><body><p id="p"><a href="https://link.com/">Simple text in English.</a></p></body></html>',
    );
    const node = dom.window.document.getElementById('p');
    expect(getLinksDensity(node)).toEqual(1.0);
  });
});
