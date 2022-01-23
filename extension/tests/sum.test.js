import sum from '../scripts/get-article-nodes';

describe('Function sum', () => {
  test('adds 1 + 2 to equal 3', () => {
    expect(sum(1, 2)).toBe(3);
  });
});
