import itertools

import pytest

from smart_word_hints_api.app.text_holder import TextHolderEN


def test_basic_tokens_data__word_lemma_pos():
    raw = "I bought a house. I'm happy."
    tokens = TextHolderEN(raw).tokens
    expected = [
        ("I", "I", "PRON"),
        ("bought", "buy", "VERB"),
        ("a", "a", "DET"),
        ("house", "house", "NOUN"),
        (".", ".", "PUNCT"),
        ("I", "I", "PRON"),
        ("'m", "be", "VERB"),
        ("happy", "happy", "ADJ"),
        (".", ".", "PUNCT"),
    ]
    basic_data = [(token.text, token.lemma, token.pos) for token in tokens]
    assert basic_data == expected


@pytest.mark.parametrize(
    "text",
    [
        "The plural morpheme in English is "
        "a sibilant suffixed to the end of most nouns.",
        "A typical English verb may have five different inflected forms.",
        "The dog was barking very loudly.",
        "He does not really like us.",
    ],
)
def test_heads_are_set_correctly(text):
    tokens = TextHolderEN(text, flag_phrasal_verbs=True).tokens

    for token in tokens:
        assert token.raw_token.head.text == token.head.text


@pytest.mark.parametrize(
    "text,phrasal_verb_indices",
    [
        ("I got up early.", [(1, 2)]),
        ("I want to hang out with you.", [(3, 4)]),
        ("You should think the issue over.", [(2, 5)]),
        ("You brought that up yesterday", [(1, 3)]),
        ("Please do not give in.", [(3, 4)]),
        ("She is handing it in.", [(2, 4)]),
        ("You should think the issue over. She is handing it in.", [(2, 5), (9, 11)]),
    ],
)
def test_phrasal_verbs__with_particles(text, phrasal_verb_indices):
    tokens = TextHolderEN(text, flag_phrasal_verbs=True).tokens

    for verb_i, prt_i in phrasal_verb_indices:
        assert tokens[verb_i].is_phrasal_base_verb()
        assert tokens[verb_i].particle_token.text == tokens[prt_i].text
        assert tokens[prt_i].is_phrasal_verb_particle()
        assert tokens[prt_i].head.text == tokens[verb_i].text

    all_phrasal_verb_indices = list(itertools.chain.from_iterable(phrasal_verb_indices))
    for i in range(len(tokens)):
        if i in all_phrasal_verb_indices:
            continue
        assert not tokens[i].is_phrasal_base_verb()
        assert not tokens[i].is_phrasal_verb_prt_or_prep()


@pytest.mark.parametrize(
    "text,phrasal_verb_indices",
    [
        ("I am looking after the kids.", [(2, 3)]),
        ("I ran into the professor yesterday.", [(1, 2)]),
        ("You should always stand by her.", [(3, 4)]),
        (
            "You should always stand by her. I am looking after the kids.",
            [(3, 4), (9, 10)],
        ),
    ],
)
def test_phrasal_verbs__with_prepositions(text, phrasal_verb_indices):
    tokens = TextHolderEN(text, flag_phrasal_verbs=True).tokens

    for verb_i, prep_i in phrasal_verb_indices:
        assert tokens[verb_i].is_phrasal_base_verb()
        assert tokens[verb_i].preposition_token.text == tokens[prep_i].text
        assert tokens[prep_i].is_phrasal_verb_preposition()
        assert tokens[prep_i].head.text == tokens[verb_i].text

    all_phrasal_verb_indices = list(itertools.chain.from_iterable(phrasal_verb_indices))
    for i in range(len(tokens)):
        if i in all_phrasal_verb_indices:
            continue
        assert not tokens[i].is_phrasal_base_verb()
        assert not tokens[i].is_phrasal_verb_prt_or_prep()


@pytest.mark.parametrize(
    "text,phrasal_verb_indices",
    [
        ("You should get around to it.", [(2, 3, 4)]),
        ("He bore down on the bar.", [(1, 2, 3)]),
        (
            "You should get around to it. He bore down on the bar.",
            [(2, 3, 4), (8, 9, 10)],
        ),
    ],
)
def test_phrasal_verbs__with_particles_and_prepositions(text, phrasal_verb_indices):
    tokens = TextHolderEN(text, flag_phrasal_verbs=True).tokens

    for verb_i, prt_i, prep_i in phrasal_verb_indices:
        assert tokens[verb_i].is_phrasal_base_verb()
        assert tokens[verb_i].preposition_token.text == tokens[prep_i].text
        assert tokens[verb_i].particle_token.text == tokens[prt_i].text

        assert tokens[prep_i].is_phrasal_verb_preposition()
        assert tokens[prep_i].head.text == tokens[verb_i].text

        assert tokens[prt_i].is_phrasal_verb_particle()
        assert tokens[prt_i].head.text == tokens[verb_i].text

    all_phrasal_verb_indices = list(itertools.chain.from_iterable(phrasal_verb_indices))
    for i in range(len(tokens)):
        if i in all_phrasal_verb_indices:
            continue
        assert not tokens[i].is_phrasal_base_verb()
        assert not tokens[i].is_phrasal_verb_prt_or_prep()


@pytest.mark.parametrize(
    "text",
    [
        "You should think the issue over the winter.",
        "This sentence doesn't contain phrasal verbs.",
        "I was looking after he went here.",
        "He gave it to me in the kitchen.",
        "We must hang to have an out.",
        "I was walking by the river and fell.",
        "Look there. After you.",
    ],
)
def test_no_phrasal_verbs__are_not_detected(text):
    tokens = TextHolderEN(text, flag_phrasal_verbs=True).tokens

    for i in range(len(tokens)):
        assert not tokens[i].is_phrasal_base_verb()
        assert not tokens[i].is_phrasal_verb_prt_or_prep()
