import pytest

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


def test_word_definitions_shortening__parenthesis_at_the_beginning():
    ranking = DifficultyRankingEN()
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("The plant is an endemic species.")
    token = holder.tokens[1]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=True)
        == "a living organism lacking the power of locomotion"
    )


def test_word_definitions_shortening__parenthesis_in_the_middle():
    ranking = DifficultyRankingEN()
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("The tissue is wet.")
    token = holder.tokens[1]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=True)
        == "a soft thin paper"
    )


def test_word_definitions_shortening__parenthesis_in_the_middle__shorten_set_to_false():
    ranking = DifficultyRankingEN()
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("The tissue is wet.")
    token = holder.tokens[1]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=False)
        == "a soft thin (usually translucent) paper"
    )


@pytest.mark.parametrize(
    "definition,shortened_definition",
    [
        ("(botany) a living organism", "a living organism"),
        ("a living organism (botany)", "a living organism"),
        ("a living (at the moment) organism", "a living organism"),
        ("a living (at the moment) organism; often large", "a living organism"),
        ("a living organism; often large", "a living organism"),
        ("(botany) a living organism; often large", "a living organism"),
        ("a living organism (botany); often large", "a living organism"),
        ("a living organism; often large; sometimes small", "a living organism"),
    ],
)
def test_get_shortened_definition(definition, shortened_definition):
    assert (
        DefinitionProviderEN.get_shortened_definition(definition)
        == shortened_definition
    )
