from smart_word_hints_api.app.constants import EN_FREQUENCY_RANKING_PATH


class DifficultyRanking(dict):
    def is_hard(self, word: str, max_difficulty: int) -> bool:
        try:
            return self[word] > max_difficulty
        except KeyError:
            return False


class DifficultyRankingEN(DifficultyRanking):
    def __init__(self):
        super().__init__()
        with open(EN_FREQUENCY_RANKING_PATH, "r") as f:
            for i, word in enumerate(f.read().splitlines()):
                self[word] = i
