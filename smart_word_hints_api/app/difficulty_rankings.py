from __future__ import annotations

import csv
from pathlib import Path

from smart_word_hints_api.app.constants import (
    EN_AMALGUM_FREQUENCY_RANKING_RELATIVE_PATH,
    EN_FREQUENCY_RANKING_RELATIVE_PATH,
)


class DifficultyRankingEN(object):
    def __init__(self) -> None:
        self.sense_key__to__ranking_score: dict[str, int] = {}
        self.lemma_pos__to__first_ranking_score: dict[tuple[str, str], int] = {}
        self.lemma__to__first_ranking_score: dict[str, int] = {}

        amalgum_freq_ranking_path = (
            Path(__file__).parent / EN_AMALGUM_FREQUENCY_RANKING_RELATIVE_PATH
        )
        with open(amalgum_freq_ranking_path, "r") as f:
            csv_reader = csv.DictReader(f, delimiter="|")
            for i, row in enumerate(csv_reader):
                self.sense_key__to__ranking_score[row["key"]] = i
                self.lemma_pos__to__first_ranking_score.setdefault(
                    (row["lemma"].lower(), row["pos"]), i
                )

        naive_freq_ranking_path = (
            Path(__file__).parent / EN_FREQUENCY_RANKING_RELATIVE_PATH
        )
        with open(naive_freq_ranking_path, "r") as f:
            for i, word in enumerate(f.read().splitlines()):
                self.lemma__to__first_ranking_score[word.lower()] = i

    def get_ranking_score(self, sense_key: str, lemma: str, pos: str) -> int | None:
        ranking_by_sense_key = self.sense_key__to__ranking_score.get(sense_key)
        if ranking_by_sense_key is not None:
            return ranking_by_sense_key

        lemma_lowercase = lemma.lower()
        ranking_by_lemma_pos = self.lemma_pos__to__first_ranking_score.get(
            (lemma_lowercase, pos)
        )
        if ranking_by_lemma_pos is not None:
            return ranking_by_lemma_pos

        return self.lemma__to__first_ranking_score.get(lemma_lowercase)
