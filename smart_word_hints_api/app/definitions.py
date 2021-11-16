import re
from typing import Optional

from nltk.corpus.reader import Synset
from pywsd.lesk import adapted_lesk

from smart_word_hints_api.app.constants import LEMMATIZABLE_EN_POS_TO_POS_SIMPLE
from smart_word_hints_api.app.difficulty_rankings import DifficultyRanking
from smart_word_hints_api.app.text_holder import TextHolderEN
from smart_word_hints_api.app.token_wrappers import TokenEN


class DefinitionProviderEN:
    MAX_REASONABLE_DEFINITION_LENGTH: int = 50

    def __init__(
        self,
        difficulty_ranking: DifficultyRanking,
        max_reasonable_length: Optional[int] = None,
    ):
        self.difficulty_ranking = difficulty_ranking
        self.max_reasonable_length = (
            max_reasonable_length or self.MAX_REASONABLE_DEFINITION_LENGTH
        )

    def _get_synonym_if_easy(
        self, word: str, synset: Synset, difficulty: int
    ) -> Optional[str]:
        for synonym_lemma in synset.lemmas():
            synonym = synonym_lemma.name()
            if synonym == word:
                continue
            if not self.difficulty_ranking.is_hard(synonym, difficulty):
                return synonym
        return None

    def _get_disambiguated_synset(self, token: TokenEN, text: TextHolderEN) -> Synset:
        simple_pos = LEMMATIZABLE_EN_POS_TO_POS_SIMPLE[token.tag]
        return adapted_lesk(
            context_sentence=text.raw_text, ambiguous_word=token.text, pos=simple_pos
        )

    @staticmethod
    def get_shortened_definition(definition: str) -> str:
        without_parentheses = re.sub(r"\([^)]*\)", "", definition)
        without_subtext_after_semicolon = without_parentheses.split(";")[0]
        return without_subtext_after_semicolon.strip()

    def get_definition(
        self,
        token: TokenEN,
        text: TextHolderEN,
        difficulty: int,
        use_synonyms: bool = True,
        shorten: bool = True,
    ) -> Optional[str]:

        synset = self._get_disambiguated_synset(token, text)
        if synset is None:
            return None
        definition = synset.definition()

        if shorten:
            definition = self.get_shortened_definition(definition)

        if len(definition) <= self.max_reasonable_length:
            return definition

        if use_synonyms:
            easy_synonym = self._get_synonym_if_easy(token.lemma, synset, difficulty)
            if easy_synonym is not None:
                return easy_synonym

        return definition
