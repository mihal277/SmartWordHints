from dataclasses import dataclass
from typing import List, Optional

from smart_word_hints_api.app.definitions import DefinitionProviderEN
from smart_word_hints_api.app.difficulty_rankings import DifficultyRankingEN
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
    def __init__(self):
        self.difficulty_ranking = DifficultyRankingEN()
        self.definitions_provider = DefinitionProviderEN(self.difficulty_ranking)

    def get_hint(
        self, token: TokenEN, text: TextHolderEN, difficulty: int
    ) -> Optional[Hint]:
        try:
            ranking = self.difficulty_ranking[token.lemma]
            return Hint(
                word=token.text,
                start_position=token.start_position,
                end_position=token.end_position,
                ranking=ranking,
                definition=self.definitions_provider.get_definition(
                    token, text, difficulty
                ),
                part_of_speech=token.tag,
            )
        except ValueError:
            return None

    def get_hints(self, article: str, difficulty: int) -> List[Hint]:
        text = TextHolderEN(article)
        hints = []
        for token in text.tokens:
            if not token.is_translatable():
                continue
            if self.difficulty_ranking.is_hard(token.lemma, difficulty):
                hint = self.get_hint(token, text, difficulty)
                if hint is not None:
                    hints.append(hint)
        return hints
