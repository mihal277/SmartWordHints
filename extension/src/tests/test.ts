/**
 * @jest-environment jsdom
 */

import * as fs from 'fs';
import * as path from 'path';
import { Hint, parseApiResponse } from '../scripts/hint';
import getOuterHTMLUpdatedWithHints from '../scripts/html-manipulation';

describe('Test injecting hints', () => {
  test('test getOuterHTMLUpdatedWithHints with simple text', () => {
    const articleNode = document.createElement('p');
    articleNode.innerHTML = '  This is an <a href="abc.com">article</a>.';

    const hints = [
      new Hint({
        word: 'is',
        start_position: 5,
        end_position: 7,
        definition: 'equal; same as',
        part_of_speech: 'VBZ',
        difficulty_ranking: 208,
        wordnet_sense: 'be%2:42:06::',
      }),
      new Hint({
        word: 'article',
        start_position: 11,
        end_position: 18,
        definition: 'A piece of writing in a magazine, newspaper, or book that gives information about a topic',
        part_of_speech: 'NN',
        difficulty_ranking: 372,
        wordnet_sense: 'article%1:10:00::',
      }),
    ];

    const expected = '<p>  This <ruby>is<rp>(</rp><rt style="font-size:0.8em">equal; same as</rt><rp>)</rp></ruby> an <a href="abc.com"><ruby>article<rp>(</rp><rt style="font-size:0.8em">A piece of writing in a magazine, newspaper, or book that gives information about a topic</rt><rp>)</rp></ruby></a>.</p>';

    const result = getOuterHTMLUpdatedWithHints(hints, articleNode, 100);

    expect(result).toBe(expected);
  });

  test('test getOuterHTMLUpdatedWithHints with no hints from api', () => {
    const articleNode = document.createElement('p');
    articleNode.innerHTML = 'S0me_ g1bberish';

    const hints: Hint[] = [];

    const expected = '<p>S0me_ g1bberish</p>';

    const result = getOuterHTMLUpdatedWithHints(hints, articleNode, 100);

    expect(result).toBe(expected);
  });

  test('test getOuterHTMLUpdatedWithHints with a wikipedia article', () => {
    const inputTestFileName = 'wikipedia-article-inner-html-input.html';
    const hintsApiResponseContentFileName = 'wikipedia-article-hints-response.json';
    const outputHTMLFileName = 'wikipedia-article-outer-html-output-with-hints.html';

    const articleNode = document.createElement('p');
    articleNode.innerHTML = fs.readFileSync(path.join(__dirname, inputTestFileName), 'utf-8');
    const hints: Hint[] = parseApiResponse(
      JSON.parse(fs.readFileSync(path.join(__dirname, hintsApiResponseContentFileName), 'utf-8')),
    );

    const expected = fs.readFileSync(path.join(__dirname, outputHTMLFileName), 'utf-8');

    const result = getOuterHTMLUpdatedWithHints(hints, articleNode, 3000);

    expect(result).toBe(expected);
  });
});
