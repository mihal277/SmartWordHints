/*
 * This algorithm is more or less based on https://github.com/ageitgey/node-unfluff
 */

import allStopwords from './stopwords.json';

function getLang(doc) {
  const lang = doc.getElementsByTagName('html')[0]?.getAttribute('lang');
  if ((!lang) || (lang.length < 2)) return null;
  const isoLangCode = lang.substring(0, 2).toLowerCase();
  if (/^[a-z]{2}$/.test(isoLangCode)) return lang;
  return null;
}

function getWordStats(content, lang = 'en') {
  const removePunctuation = (text) => text.replace(/[|@<>[\]"'.,-/#?!$%^&*+;:{}=\-_`~()]/g, '');
  const stopwords = allStopwords[lang];
  const contentWords = removePunctuation(content).split(' ');
  const stopwordsUsedInContent = contentWords.filter((word) => stopwords.includes(word));
  return {
    wordCount: contentWords.length,
    stopwordCount: stopwordsUsedInContent.length,
    stopWords: stopwordsUsedInContent,
  };
}

function getLinksDensity(node) {
  const links = [...node.querySelectorAll('a')];
  if (links.length === 0) { return 0.0; }
  const linkWordsLength = links.map((i) => i.text).join(' ').split(' ').length;
  const allTextLength = node.textContent.split(' ').length;
  return linkWordsLength / allTextLength;
}

function getBestNode(doc, lang) {
  const nodes = doc.querySelectorAll('p, pre, td');
}

export default function getArticleNodes(doc, lang) {
  const language = lang || getLang();
}

export const exportedForTesting = {
  getLang, getWordStats, getLinksDensity,
};
