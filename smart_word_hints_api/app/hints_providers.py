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

    def get_hint(
        self, token: TokenEN, text: TextHolderEN, difficulty: int
    ) -> Optional[Hint]:
        try:
            ranking = self.difficulty_ranking[token.lemma]
            definition = self.definitions_provider.get_definition(
                token, text, difficulty
            )
            if definition is None:
                return None
            return Hint(
                word=token.text,
                start_position=token.start_position,
                end_position=token.end_position,
                ranking=ranking,
                definition=definition,
                part_of_speech=token.tag,
            )
        except ValueError:
            return None

    @staticmethod
    def would_be_a_repetition(
        token: TokenEN, already_hinted: set[tuple[str, str]]
    ) -> bool:
        return (token.lemma, token.tag) in already_hinted

    def should_skip(
        self,
        token: TokenEN,
        already_hinted: set[tuple[str, str]],
        avoid_repetitions: bool,
        difficulty: int,
    ) -> bool:
        if not token.is_translatable():
            return True
        if avoid_repetitions and self.would_be_a_repetition(token, already_hinted):
            return True
        if not self.difficulty_ranking.is_hard(token.lemma, difficulty):
            return True
        return False

    def get_hints(
        self, article: str, difficulty: int, avoid_repetitions: bool = True
    ) -> list[Hint]:
        text = TextHolderEN(article)
        hints = []
        already_hinted_lemma_tag_set: set[tuple[str, str]] = set()
        for token in text.tokens:
            if self.should_skip(
                token, already_hinted_lemma_tag_set, avoid_repetitions, difficulty
            ):
                continue
            hint = self.get_hint(token, text, difficulty)
            if hint is not None:
                hints.append(hint)
                already_hinted_lemma_tag_set.add((token.lemma, token.tag))
        return hints
