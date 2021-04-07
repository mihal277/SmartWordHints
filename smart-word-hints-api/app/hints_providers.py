from dataclasses import dataclass
from typing import List, Tuple, Optional, Generator, Union

from nltk import tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

from constants import EN_FREQUENCY_RANKING_PATH, LEMMATIZABLE_POS_TO_POS_SIMPLE


@dataclass
class Hint:
    word: str
    start_position: int
    end_position: int
    ranking: int
    definition: int


class EnglishToEnglishHintsProvider:
    def __init__(self):
        self.freq_ranking = self.load_words_frequency_ranking_en()
        self.lemmatizer = WordNetLemmatizer()
        self.tokenize = tokenize.word_tokenize
        self.tag_pos = pos_tag

    @staticmethod
    def load_words_frequency_ranking_en() -> List[str]:
        with open(EN_FREQUENCY_RANKING_PATH, "r") as f:
            return f.read().splitlines()

    def get_tokens_with_spans(
        self, text: str
    ) -> Generator[Tuple[str, int, int], None, None]:
        tokens = self.tokenize(text)
        offset = 0
        for token in tokens:
            offset = text.find(token, offset)
            yield token, offset, offset + len(token)
            offset += len(token)

    def get_lemma(self, word: str, part_of_speech: str) -> str:
        pos_simple = LEMMATIZABLE_POS_TO_POS_SIMPLE.get(part_of_speech)
        if pos_simple is None:
            return word
        return self.lemmatizer.lemmatize(word, pos_simple)

    @staticmethod
    def preprocess_input_words(words: List[str]) -> List[str]:
        return [word.lower() if word != "I" else word for word in words]

    def get_lemmas(
        self, words: List[str], return_with_pos: bool
    ) -> Union[List[str], List[Tuple[str, str]]]:
        preprocessed = self.preprocess_input_words(words)
        words_with_pos = self.tag_pos(preprocessed)
        if return_with_pos:
            return [(self.get_lemma(word, pos), pos) for word, pos in words_with_pos]
        return [self.get_lemma(word, pos) for word, pos in words_with_pos]

    def get_hint(self, word: str, start: int, end: int, pos: str) -> Optional[Hint]:
        try:
            simple_pos = LEMMATIZABLE_POS_TO_POS_SIMPLE.get(pos)
            definition = wordnet.synsets(word, simple_pos)[0].definition()
            ranking = self.freq_ranking.index(word)
            return Hint(
                word=word,
                start_position=start,
                end_position=end,
                ranking=ranking,
                definition=definition,
            )
        except (IndexError, ValueError):
            return None

    def get_hints(self, article: str, difficulty: int) -> List[Hint]:
        most_common = self.freq_ranking[:difficulty]
        words_with_spans = list(self.get_tokens_with_spans(article))
        words = [word for word, _, _ in words_with_spans]
        hints = []
        for (_, start, end), (lemma, pos) in zip(
            words_with_spans, self.get_lemmas(words, return_with_pos=True)
        ):
            if lemma not in most_common:
                hint = self.get_hint(lemma, start, end, pos)
                if hint is not None:
                    hints.append(hint)
        return hints
