from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional, TypedDict

from nltk.corpus import wordnet as wn
from nltk.corpus.reader import Synset

from smart_word_hints_api.app.constants import (
    EN_SIMPLE_DEFINITIONS_RELATIVE_PATH,
    MAX_FREQUENCY_RANKING_SCORE_TO_CONSIDER_AS_EASY,
)
from smart_word_hints_api.app.difficulty_rankings import DifficultyRankingEN
from smart_word_hints_api.app.token_wrappers import TokenEN


class Definitions(TypedDict):
    simplified: str
    original_wordnet: str


class DefinitionProviderEN:
    def __init__(self, difficulty_ranking: DifficultyRankingEN) -> None:
        self.sense_key__to__definitions: dict[
            str, Definitions
        ] = self._load_sense_key__to__definitions_mapping()
        self.max_reasonable_length_for_wordnet_definition: int = 50
        self.difficulty_ranking = difficulty_ranking

    def get_definition(
        self,
        token: TokenEN,
        token_sense_key: str,
        add_prefix_if_phrasal_verb: bool = True,
    ) -> Optional[str]:
        definitions: Definitions = self.sense_key__to__definitions.get(token_sense_key)
        if definitions is not None:
            return self._postprocess_definition(
                token, definitions["simplified"], add_prefix_if_phrasal_verb
            )

        return self._get_definition_using_wordnet(
            token, token_sense_key, add_prefix_if_phrasal_verb
        )

    def _load_sense_key__to__definitions_mapping(self) -> dict[str, Definitions]:
        simple_definitions_path = (
            Path(__file__).parent / EN_SIMPLE_DEFINITIONS_RELATIVE_PATH
        )
        with open(simple_definitions_path, "r") as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            return {
                row["key"]: Definitions(
                    simplified=self._clean_simple_definition(row["simple_definition"]),
                    original_wordnet=row["original_definition"],
                )
                for row in csv_reader
            }

    @staticmethod
    def _clean_simple_definition(dirty_simple_definition: str) -> str:
        split_by_equal_sign = dirty_simple_definition.split(" = ")
        if len(split_by_equal_sign) == 1:
            return split_by_equal_sign[0]
        return "".join(split_by_equal_sign[1:])

    def _get_definition_using_wordnet(
        self, token: TokenEN, token_sense_key: str, add_prefix_if_phrasal_verb: bool
    ) -> str:
        synset = wn.synset_from_sense_key(token_sense_key)
        definition = self._get_shortened_definition(synset.definition())

        if len(definition) <= self.max_reasonable_length_for_wordnet_definition:
            return self._postprocess_definition(
                token, definition, add_prefix_if_phrasal_verb
            )

        easy_synonym = self._get_synonym_if_easy(token.lemma, synset)
        if easy_synonym is not None:
            return self._postprocess_definition(
                token, easy_synonym, add_prefix_if_phrasal_verb
            )
        return self._postprocess_definition(
            token, definition, add_prefix_if_phrasal_verb
        )

    def _get_synonym_if_easy(self, word: str, synset: Synset) -> Optional[str]:
        for synonym_lemma in synset.lemmas():
            if synonym_lemma.name() == word:
                continue
            ranking_score: int | None = self.difficulty_ranking.get_ranking_score(
                synonym_lemma.key(), synonym_lemma.name(), synset.pos()
            )
            if ranking_score is None:
                return None
            if ranking_score < MAX_FREQUENCY_RANKING_SCORE_TO_CONSIDER_AS_EASY:
                return synonym_lemma.name()
        return None

    @staticmethod
    def _get_shortened_definition(definition: str) -> str:
        without_parentheses = re.sub(r"\([^)]*\)", "", definition).replace("  ", " ")
        without_subtext_after_semicolon = without_parentheses.split(";")[0]
        return without_subtext_after_semicolon.strip()

    def _postprocess_definition(
        self, token: TokenEN, definition: str, add_prefix_if_phrasal_verb: bool
    ) -> str:
        if add_prefix_if_phrasal_verb and token.is_phrasal_base_verb():
            return f"{token.lemma_extended} = {definition}"
        return definition
