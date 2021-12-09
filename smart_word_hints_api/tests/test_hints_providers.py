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


def test_uppercase_word__noun():
    hints_provider = EnglishToEnglishHintsProvider(
        difficulty_ranking=DifficultyRanking({"prophet": 1500})
    )
    actual = hints_provider.get_hints("I don't know the Prophet.", 1000)
    expected = [
        Hint(
            word="Prophet",
            start_position=17,
            end_position=24,
            ranking=1500,
            definition="someone who speaks by divine inspiration",
            part_of_speech="NNP",
        )
    ]

    assert actual == expected


def test_uppercase_word__verb():
    hints_provider = EnglishToEnglishHintsProvider(
        difficulty_ranking=DifficultyRanking({"build": 1500})
    )
    actual = hints_provider.get_hints("I Build The House.", 1000)
    expected = [
        Hint(
            word="Build",
            start_position=2,
            end_position=7,
            ranking=1500,
            definition="make by combining materials and parts",
            part_of_speech="VBP",
        )
    ]

    assert actual == expected


def test_hints_with_phrasal_verbs__particle():
    hints_provider = EnglishToEnglishHintsProvider(
        difficulty_ranking=DifficultyRanking({"pull": 1500})
    )
    actual = hints_provider.get_hints("Pull over, sir.", 1000)
    expected = [
        Hint(
            word="Pull over",
            start_position=0,
            end_position=4,
            ranking=1500,
            definition="steer a vehicle to the side of the road",
            part_of_speech="VB",
        )
    ]

    assert actual == expected


def test_hints_with_phrasal_verbs__preposition():
    hints_provider = EnglishToEnglishHintsProvider(
        difficulty_ranking=DifficultyRanking({"look": 1500})
    )
    actual = hints_provider.get_hints("I am looking after the kids.", 1000)
    expected = [
        Hint(
            word="looking after",
            start_position=5,
            end_position=12,
            ranking=1500,
            definition="keep under careful scrutiny",
            part_of_speech="VBG",
        )
    ]

    assert actual == expected


def test_hints_with_phrasal_verbs__particle_with_preposition():
    hints_provider = EnglishToEnglishHintsProvider(
        difficulty_ranking=DifficultyRanking({"get": 1500})
    )
    actual = hints_provider.get_hints("You should get around to it.", 1000)
    expected = [
        Hint(
            word="get around to",
            start_position=11,
            end_position=14,
            ranking=1500,
            definition="do something despite obstacles such as lack of time",
            part_of_speech="VB",
        )
    ]

    assert actual == expected
