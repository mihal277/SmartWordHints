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


def test_synonym_is_not_returned_if_it_is_unknown_in_the_ranking():
    difficulty_ranking = DifficultyRanking({"auto": 1500})
    definition_provider = DefinitionProviderEN(
        difficulty_ranking, max_reasonable_length=50
    )
    text = TextHolderEN("I bought a new auto.")
    definition = definition_provider.get_definition(
        text.tokens[4], text, 1000, use_synonyms=True, shorten=True
    )
    assert definition == "a motor vehicle with four wheels"


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
        DefinitionProviderEN._get_shortened_definition(definition)
        == shortened_definition
    )


def test_phrasal_verb_correctly_translated__particle():
    ranking = DifficultyRanking({"shut": 1500})
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("You should shut up.", flag_phrasal_verbs=True)
    token = holder.tokens[2]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=True)
        == "refuse to talk or stop talking"
    )


def test_phrasal_verb_correctly_translated__preposition():
    ranking = DifficultyRanking({"care": 1500})
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("She says he never cared for her.", flag_phrasal_verbs=True)
    token = holder.tokens[4]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=True)
        == "provide treatment for"
    )


def test_phrasal_verb_correctly_translated__particle_with_preposition():
    ranking = DifficultyRanking({"get": 1500})
    provider = DefinitionProviderEN(ranking)
    holder = TextHolderEN("You should get around to it.", flag_phrasal_verbs=True)
    token = holder.tokens[2]
    assert (
        provider.get_definition(token, holder, 1000, use_synonyms=False, shorten=True)
        == "do something despite obstacles such as lack of time"
    )
