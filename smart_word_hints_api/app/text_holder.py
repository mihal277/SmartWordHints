from __future__ import annotations

import functools
from typing import Optional

import spacy

from smart_word_hints_api.app.token_wrappers import TokenEN

nlp_en = spacy.load("en_core_web_sm")


class TextHolderEN:
    def __init__(self, text: str, flag_phrasal_verbs: bool = False):
        self.raw_text = text
        self.doc = nlp_en(text)
        if flag_phrasal_verbs:
            self.flag_phrasal_verb_base_verbs()

    @staticmethod
    def _set_head_for_each_token(tokens: list[TokenEN]) -> None:
        for token in tokens:
            token._head = tokens[token.raw_token.head.i]

    @functools.cached_property
    def tokens(self) -> list[TokenEN]:
        result: list[TokenEN] = []
        offset = 0
        for token_raw in self.doc:
            offset = self.raw_text.find(token_raw.text, offset)
            result.append(
                TokenEN(
                    token_raw,
                    start_position=offset,
                    end_position=offset + len(token_raw.text),
                )
            )
            offset += len(token_raw.text)
        self._set_head_for_each_token(result)
        return result

    def _tag_all_tokens_as_non_phrasal_verb_base(self) -> None:
        for token in self.tokens:
            token._is_phrasal_verb_base_verb = False

    @staticmethod
    def _get_prt_or_prep_for_a_given_verb(
        verb_token: TokenEN, prt_prep_set: set[TokenEN]
    ) -> Optional[TokenEN]:
        for prt_or_prep in prt_prep_set:
            if prt_or_prep.head.text != verb_token.text:
                continue
            return prt_or_prep
        return None

    def _flag_particle_phrasal_verbs(self) -> None:
        particle_tokens = set()
        for token in reversed(self.tokens):
            if token.is_phrasal_verb_particle():
                particle_tokens.add(token)
            elif token.is_verb():
                particle_for_the_verb = self._get_prt_or_prep_for_a_given_verb(
                    token, particle_tokens
                )
                if particle_for_the_verb is None:
                    continue
                token.flag_as_phrasal_base_verb(particle_token=particle_for_the_verb)
                particle_tokens.remove(particle_for_the_verb)

    def _flag_prepositional_phrasal_verbs(self) -> None:
        """
        Finding prepositions has to take place after finding particles
        because when establishing if a preposition is a part of
        a verb+particle+preposition phrasal verb, the particle has
        to be known already.
        """
        preposition_tokens = set()
        for token in reversed(self.tokens):
            if token.is_phrasal_verb_preposition():
                preposition_tokens.add(token)
            elif token.is_verb():
                preposition_for_the_verb = self._get_prt_or_prep_for_a_given_verb(
                    token, preposition_tokens
                )
                if preposition_for_the_verb is None:
                    continue
                token.flag_as_phrasal_base_verb(
                    preposition_token=preposition_for_the_verb
                )
                preposition_tokens.remove(preposition_for_the_verb)

    def flag_phrasal_verb_base_verbs(self) -> None:
        self._tag_all_tokens_as_non_phrasal_verb_base()
        self._flag_particle_phrasal_verbs()
        self._flag_prepositional_phrasal_verbs()
