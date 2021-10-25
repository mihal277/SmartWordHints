from smart_word_hints_api.app.definitions import DefinitionProviderEN
from smart_word_hints_api.app.difficulty_rankings import DifficultyRanking


def test_an_easy_synonym_is_returned_as_definition():
    difficulty_ranking = DifficultyRanking({"car": 50, "auto": 1500})
    definition_provider = DefinitionProviderEN(difficulty_ranking)
    definition = definition_provider.get_definition(
        "auto", "NN", "I bought a new auto.", 1000
    )
    assert definition == "car"
