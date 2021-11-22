from smart_word_hints_api.app.difficulty_rankings import DifficultyRanking
from smart_word_hints_api.app.hints_providers import EnglishToEnglishHintsProvider, Hint


def test_personal_pronouns_dont_raise_exceptions__smoke_test():
    hints_provider = EnglishToEnglishHintsProvider()
    hints_provider.get_hints("You are very nice", 0)


def test_none_definition():
    hints_provider = EnglishToEnglishHintsProvider()
    assert [] == hints_provider.get_hints("You are very niceeee", 1000)


def test_hints_are_returned_with_repetitions_if_avoid_repetitions_is_false():
    hints_provider = EnglishToEnglishHintsProvider(
        difficulty_ranking=DifficultyRanking({"tissue": 1500})
    )
    actual = hints_provider.get_hints(
        "This is a tissue. The tissue is wet.", 1000, avoid_repetitions=False
    )
    expected = [
        Hint(
            word="tissue",
            start_position=10,
            end_position=16,
            ranking=1500,
            definition="a soft thin paper",
            part_of_speech="NN",
        ),
        Hint(
            word="tissue",
            start_position=22,
            end_position=28,
            ranking=1500,
            definition="a soft thin paper",
            part_of_speech="NN",
        ),
    ]

    assert actual == expected


def test_hints_are_returned_without_repetitions_if_avoid_repetitions_is_true():
    hints_provider = EnglishToEnglishHintsProvider(
        difficulty_ranking=DifficultyRanking({"tissue": 1500})
    )
    actual = hints_provider.get_hints(
        "This is a tissue. The tissue is wet.", 1000, avoid_repetitions=True
    )
    expected = [
        Hint(
            word="tissue",
            start_position=10,
            end_position=16,
            ranking=1500,
            definition="a soft thin paper",
            part_of_speech="NN",
        )
    ]

    assert actual == expected
