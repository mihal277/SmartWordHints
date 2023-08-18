from __future__ import annotations

from dataclasses import dataclass

from smart_word_hints_api.app.config import config
from smart_word_hints_api.app.constants import CONFIG_KEY_MODEL_NAME
from smart_word_hints_api.app.definitions import DefinitionProviderEN
from smart_word_hints_api.app.difficulty_rankings import DifficultyRankingEN
from smart_word_hints_api.app.esr_sense_provider import ESRSenseProvider
from smart_word_hints_api.app.text_holder import TextHolderEN


@dataclass(frozen=True)
class Hint:
    word: str
    start_position: int
    end_position: int
    definition: str
    part_of_speech: str
    difficulty_ranking: int
    wordnet_sense: str


class EnglishToEnglishHintsProvider:
    def __init__(self):
        self.difficulty_ranking = DifficultyRankingEN()
        self.sense_provider = ESRSenseProvider(config.get(CONFIG_KEY_MODEL_NAME))
        self.definitions_provider = DefinitionProviderEN(self.difficulty_ranking)

    def get_hints(self, text: str, avoid_repetitions: bool = True) -> list[Hint]:
        text_holder = TextHolderEN(text, flag_phrasal_verbs=True)

        token_indexes_to_disambiguate = []
        for i, token in enumerate(text_holder.tokens):
            if token.is_translatable():
                token_indexes_to_disambiguate.append(i)

        token_i__to__sense_key: dict[i, str] = self.sense_provider.get_sense_keys(
            text_holder, token_indexes_to_disambiguate
        )
        hints: list[Hint] = self._get_hints(text_holder, token_i__to__sense_key)

        if avoid_repetitions:
            hints = self._deduplicate_hints(hints)

        return hints

    def _get_hints(
        self, text_holder: TextHolderEN, token_i__to__sense_key: dict[int, str]
    ) -> list[Hint]:
        hints = []
        for token_i, token in enumerate(text_holder.tokens):
            if token_i not in token_i__to__sense_key:
                continue
            sense_key = token_i__to__sense_key[token_i]
            difficulty_ranking = self.difficulty_ranking.get_ranking_score(
                sense_key, token.lemma, token.pos_simple
            )
            definition = self.definitions_provider.get_definition(token, sense_key)
            hint = Hint(
                word=token.text_extended,
                start_position=token.start_position,
                end_position=token.end_position_extended,
                definition=definition,
                part_of_speech=token.tag,
                difficulty_ranking=difficulty_ranking,
                wordnet_sense=sense_key,
            )
            hints.append(hint)
        return hints

    @staticmethod
    def _deduplicate_hints(hints: list[Hint]) -> list[Hint]:
        deduplicated: list[Hint] = []
        already_used_senses: set[str] = set()
        for hint in hints:
            if hint.wordnet_sense not in already_used_senses:
                deduplicated.append(hint)
            already_used_senses.add(hint.wordnet_sense)
        return deduplicated
