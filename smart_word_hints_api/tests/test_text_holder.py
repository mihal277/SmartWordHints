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
    "text,phrasal_verb_indices",
    [
        ("I got up early. Then I got a present.", [(1, 2)]),
        ("Then I got a present. I got up early.", [(7, 8)]),
        (
            "I want to hang out with you. We must hang to have an out.",
            [(3, 4)],
        ),
        (
            "We must hang to have an out. I want to hang out with you.",
            [(11, 12)],
        ),
        ("You should think the issue over. Think about it over the winter.", [(2, 5)]),
        ("Think about it over the winter. You should think the issue over.", [(9, 12)]),
        ("I was walking by the river and fell.", []),
    ],
)
def test_phrasal_verbs(text, phrasal_verb_indices):
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
        assert not tokens[i].is_phrasal_verb_particle()
