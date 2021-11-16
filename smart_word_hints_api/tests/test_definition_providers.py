from smart_word_hints_api.app.definitions import DefinitionProviderEN
from smart_word_hints_api.app.difficulty_rankings import (
    DifficultyRanking,
    DifficultyRankingEN,
)
from smart_word_hints_api.app.text_holder import TextHolderEN


def test_an_easy_synonym_is_returned_as_definition():
    difficulty_ranking = DifficultyRanking({"car": 50, "auto": 1500})
    definition_provider = DefinitionProviderEN(
        difficulty_ranking, max_reasonable_length=50
    )
    text = TextHolderEN("I bought a new auto.")
    definition = definition_provider.get_definition(
        text.tokens[4], text, 1000, use_synonyms=True, shorten=False
    )
    assert definition == "car"


def test_word_plant_is_correctly_disambiguated():
    ranking = DifficultyRanking({"plant": 1500})
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("The plant is an endemic species.")
    token = holder.tokens[1]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=False)
        == "(botany) a living organism lacking the power of locomotion"
    )


def test_word_definitions_shortening():
    ranking = DifficultyRankingEN()
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("The plant is an endemic species.")
    token = holder.tokens[1]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=True)
        == "a living organism lacking the power of locomotion"
    )
