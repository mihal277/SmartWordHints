from itertools import chain
from typing import Dict, List, Optional, Set

from nltk.corpus import wordnet
from nltk.corpus.reader import Synset

from smart_word_hints_api.app.constants import (
    ADJECTIVES,
    LEMMATIZABLE_POS_TO_POS_SIMPLE,
)
from smart_word_hints_api.app.difficulty_rankings import DifficultyRanking


class DefinitionProviderEN:
    MAX_REASONABLE_DEFINITION_LENGTH: int = 50

    def __init__(
        self,
        difficulty_ranking: DifficultyRanking,
        max_reasonable_length: Optional[int] = None,
    ):
        self.synsets = self._load_synsets()
        self.difficulty_ranking = difficulty_ranking
        self.max_reasonable_length = (
            max_reasonable_length or self.MAX_REASONABLE_DEFINITION_LENGTH
        )

    @staticmethod
    def _load_synsets() -> Dict[str, List[Synset]]:
        print("Loading synsets...")
        lemmas_in_wordnet: Set[str] = set(
            chain(*[x.lemma_names() for x in wordnet.all_synsets()])
        )
        return {lemma: wordnet.synsets(lemma) for lemma in lemmas_in_wordnet}

    @staticmethod
    def _same_pos(pos1: str, pos2: str) -> bool:
        if pos1 in ADJECTIVES:
            return pos2 in ADJECTIVES
        return pos1 == pos2

    def _get_synsets(self, word: str, pos_simple: str) -> List[Synset]:
        synsets = self.synsets.get(word, [])
        return [
            synset for synset in synsets if self._same_pos(synset.pos(), pos_simple)
        ]

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

    def _get_disambiguated_synset(self, word: str, pos: str, article: str) -> Synset:
        simple_pos = LEMMATIZABLE_POS_TO_POS_SIMPLE[pos]
        #  TODO: what about multithreading?
        # return lesk(article.split(), word, pos=simple_pos)
        return self._get_synsets(word, simple_pos)[0]

    def get_definition(
        self, word: str, pos: str, article: str, difficulty: int
    ) -> Optional[str]:
        try:
            synset = self._get_disambiguated_synset(word, pos, article)
            definition = synset.definition()
            if len(definition) > self.max_reasonable_length:
                easy_synonym = self._get_synonym_if_easy(word, synset, difficulty)
                if easy_synonym is not None:
                    return easy_synonym
            return definition
        except IndexError:
            return None
