from dataclasses import dataclass
from typing import Optional

from smart_word_hints_api.app.definitions import DefinitionProviderEN
from smart_word_hints_api.app.difficulty_rankings import (
    DifficultyRanking,
    DifficultyRankingEN,
)
from smart_word_hints_api.app.text_holder import TextHolderEN, TokenEN


@dataclass
class Hint:
    word: str
    start_position: int
    end_position: int
    ranking: int
    definition: str
    part_of_speech: str


class EnglishToEnglishHintsProvider:
    def __init__(self, difficulty_ranking: DifficultyRanking = None):
        self.difficulty_ranking = difficulty_ranking or DifficultyRankingEN()
        self.definitions_provider = DefinitionProviderEN(self.difficulty_ranking)

    @staticmethod
    def _get_word_which_is_hinted(token: TokenEN) -> str:
        if token.is_phrasal_base_verb():
            return f"{token.text} {token.particle_token.text}"
        return token.text

    def _get_hint(
        self, token: TokenEN, text: TextHolderEN, difficulty: int
    ) -> Optional[Hint]:
        ranking = self.difficulty_ranking[token.lemma.lower()]
        definition = self.definitions_provider.get_definition(token, text, difficulty)
        if definition is None:
            return None
        return Hint(
            word=self._get_word_which_is_hinted(token),
            start_position=token.start_position,
            end_position=token.end_position,
            ranking=ranking,
            definition=definition,
            part_of_speech=token.tag,
        )

    @staticmethod
    def _would_be_a_repetition(
        token: TokenEN, already_hinted: set[tuple[str, str]]
    ) -> bool:
        return (token.lemma, token.tag) in already_hinted

    def _should_skip(
        self,
        token: TokenEN,
        already_hinted: set[tuple[str, str]],
        avoid_repetitions: bool,
        difficulty: int,
    ) -> bool:
        if not token.is_translatable():
            return True
        if avoid_repetitions and self._would_be_a_repetition(token, already_hinted):
            return True
        difficulty_result = self.difficulty_ranking.check(
            token.lemma.lower(), difficulty
        )
        if difficulty_result.easy_or_unknown():
            return True
        return False

    def get_hints(
        self, article: str, difficulty: int, avoid_repetitions: bool = True
    ) -> list[Hint]:
        text = TextHolderEN(article, flag_phrasal_verbs=True)
        hints = []
        already_hinted_lemma_tag_set: set[tuple[str, str]] = set()
        for token in text.tokens:
            if self._should_skip(
                token, already_hinted_lemma_tag_set, avoid_repetitions, difficulty
            ):
                continue
            hint = self._get_hint(token, text, difficulty)
            if hint is not None:
                hints.append(hint)
                already_hinted_lemma_tag_set.add((token.lemma, token.tag))
        return hints
