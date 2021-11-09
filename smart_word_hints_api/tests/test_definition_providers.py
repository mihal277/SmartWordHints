from smart_word_hints_api.app.definitions import DefinitionProviderEN
from smart_word_hints_api.app.difficulty_rankings import DifficultyRanking
from smart_word_hints_api.app.text_holder import TextHolderEN


def test_an_easy_synonym_is_returned_as_definition():
    difficulty_ranking = DifficultyRanking({"car": 50, "auto": 1500})
    definition_provider = DefinitionProviderEN(
        difficulty_ranking, max_reasonable_length=50
    )
    text = TextHolderEN("I bought a new auto.")
    definition = definition_provider.get_definition(text.tokens[4], text, 1000)
    assert definition == "car"
