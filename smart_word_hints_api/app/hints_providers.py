from dataclasses import dataclass
from typing import Generator, List, Optional, Tuple, Union

from nltk import pos_tag, tokenize
from nltk.stem import WordNetLemmatizer

from smart_word_hints_api.app.constants import LEMMATIZABLE_POS_TO_POS_SIMPLE
from smart_word_hints_api.app.definitions import DefinitionProviderEN
from smart_word_hints_api.app.difficulty_rankings import DifficultyRankingEN


@dataclass
class Hint:
    word: str
    start_position: int
    end_position: int
    ranking: int
    definition: str
    part_of_speech: str


class EnglishToEnglishHintsProvider:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.tokenize = tokenize.word_tokenize
        self.tag_pos = pos_tag
        self.difficulty_ranking = DifficultyRankingEN()
        self.definitions_provider = DefinitionProviderEN(self.difficulty_ranking)

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

    def get_hint(
        self, word: str, start: int, end: int, pos: str, article: str, difficulty: int
    ) -> Optional[Hint]:
        try:
            ranking = self.difficulty_ranking[word]
            return Hint(
                word=word,
                start_position=start,
                end_position=end,
                ranking=ranking,
                definition=self.definitions_provider.get_definition(
                    word, pos, article, difficulty
                ),
                part_of_speech=pos,
            )
        except ValueError:
            return None

    def get_hints(self, article: str, difficulty: int) -> List[Hint]:
        words_with_spans = list(self.get_tokens_with_spans(article))
        words = [word for word, _, _ in words_with_spans]
        hints = []
        for (_, start, end), (lemma, pos) in zip(
            words_with_spans, self.get_lemmas(words, return_with_pos=True)
        ):
            if self.difficulty_ranking.is_hard(lemma, difficulty):
                hint = self.get_hint(lemma, start, end, pos, article, difficulty)
                if hint is not None:
                    hints.append(hint)
        return hints
