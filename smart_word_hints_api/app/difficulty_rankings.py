from enum import Enum

from smart_word_hints_api.app.constants import EN_FREQUENCY_RANKING_PATH


class DifficultyRankingResult(Enum):
    HARD = "hard"
    EASY = "easy"
    UNKNOWN = "unknown"

    def easy_or_unknown(self):
        return (
            self == DifficultyRankingResult.EASY
            or self == DifficultyRankingResult.UNKNOWN
        )

    def easy(self):
        return self == DifficultyRankingResult.EASY


class DifficultyRanking(dict):
    def check(self, word: str, max_difficulty: int) -> DifficultyRankingResult:
        word_ranking = self.get(word)
        if word_ranking is None:
            return DifficultyRankingResult.UNKNOWN
        if word_ranking > max_difficulty:
            return DifficultyRankingResult.HARD
        return DifficultyRankingResult.EASY


class DifficultyRankingEN(DifficultyRanking):
    def __init__(self):
        super().__init__()
        with open(EN_FREQUENCY_RANKING_PATH, "r") as f:
            for i, word in enumerate(f.read().splitlines()):
                self[word] = i
