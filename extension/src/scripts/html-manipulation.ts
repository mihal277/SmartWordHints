import { Hint } from './hint';

function decodeHtml(html: string): string {
  const txt = document.createElement('textarea');
  txt.innerHTML = html;
  return txt.value;
}

function mapIndexOfTextContentToIndexOfOuterHTML(
  textContent: string,
  outerHTMLDecoded: string,
): Record<number, number> {
  const textMapping: Record<number, number> = {};
  const textLength = textContent.length;
  let outerHTMLIndex = 0;
  let insideHTMLElement = false;

  for (let textIndex = 0; textIndex < textLength; textIndex += 1) {
    const char = textContent[textIndex];

    while (outerHTMLIndex < outerHTMLDecoded.length) {
      if (outerHTMLDecoded[outerHTMLIndex] === char && !insideHTMLElement) {
        textMapping[textIndex] = outerHTMLIndex;
        outerHTMLIndex += 1;
        break;
      }

      if (outerHTMLDecoded[outerHTMLIndex] === '<') insideHTMLElement = true;
      else if (outerHTMLDecoded[outerHTMLIndex] === '>') insideHTMLElement = false;
      outerHTMLIndex += 1;
    }
  }

  // sanity check:
  Object.keys(textMapping).forEach((textIndex: string) => {
    const textIndexInt = Number(textIndex);
    if (textContent[textIndexInt] !== outerHTMLDecoded[textMapping[textIndexInt]]) throw Error('Something went wrong with article parsing');
  });

  return textMapping;
}

export default function getOuterHTMLUpdatedWithHints(
  hints: Hint[],
  articleNode: HTMLElement,
  difficulty: number,
): string {
  const textContent = articleNode.textContent.trim();
  const { outerHTML } = articleNode;
  const outerHTMLDecoded = decodeHtml(outerHTML);

  const textToHTMLMapping = mapIndexOfTextContentToIndexOfOuterHTML(textContent, outerHTMLDecoded);

  let updatedOuterHTML = '';
  let lastEnd = 0;

  hints.forEach((hint: Hint) => {
    if (hint.difficulty_ranking < difficulty) return;
    updatedOuterHTML += outerHTMLDecoded.slice(lastEnd, textToHTMLMapping[hint.start_position]);
    const snippetToShowDefinitionFor = outerHTMLDecoded.slice(
      textToHTMLMapping[hint.start_position],
      textToHTMLMapping[hint.end_position - 1] + 1,
    );
    updatedOuterHTML += `<ruby><b>${
      snippetToShowDefinitionFor
    }</b><rp>(</rp>`
    + `<rt style="font-size:0.8em">${hint.definition}</rt>`
    + '<rp>)</rp>'
    + '</ruby>';

    lastEnd = textToHTMLMapping[hint.end_position - 1] + 1;
  });
  updatedOuterHTML += outerHTMLDecoded.slice(lastEnd, outerHTMLDecoded.length);

  // todo: encode returened HTML
  return updatedOuterHTML;
}
