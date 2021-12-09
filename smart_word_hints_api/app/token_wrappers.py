from __future__ import annotations

from typing import Optional

from spacy.tokens.token import Token

from smart_word_hints_api.app.constants import (
    LEMMATIZABLE_EN_POS_TO_POS_SIMPLE,
    TRANSLATABLE_EN_POS,
    UNIVERSAL_POS_VERB,
)
from smart_word_hints_api.app.phrasal_verbs import load_phrasal_verbs


class TokenWrapper:
    def __init__(self, spacy_token: Token, start_position: int, end_position: int):
        self.raw_token = spacy_token
        self.start_position = start_position
        self.end_position = end_position

    @property
    def text(self) -> str:
        return self.raw_token.text

    @property
    def lemma(self) -> str:
        return self.raw_token.lemma_

    @property
    def pos(self) -> str:
        return self.raw_token.pos_

    @property
    def tag(self) -> str:
        return self.raw_token.tag_

    @property
    def dep(self) -> str:
        return self.raw_token.dep_

    @property
    def i(self) -> int:
        return self.raw_token.i

    def is_verb(self):
        return self.pos == UNIVERSAL_POS_VERB


class PhrasalVerbError(Exception):
    pass


class TokenError(Exception):
    pass


PHRASAL_VERBS = load_phrasal_verbs()


class TokenEN(TokenWrapper):
    def __init__(self, spacy_token: Token, start_position: int, end_position: int):
        super().__init__(spacy_token, start_position, end_position)
        self._is_phrasal_verb_base_verb: Optional[bool] = None
        self._phrasal_verb_particle_token: Optional[TokenEN] = None
        self._phrasal_verb_preposition_token: Optional[TokenEN] = None
        self._head: Optional[TokenEN] = None

    @property
    def head(self) -> TokenEN:
        if self._head is None:
            raise TokenError("Head is not set")
        return self._head

    def _is_on_list_of_phrasal_verbs_with_particle_and_preposition(self) -> bool:
        potential_prt_prep_pv = (
            f"{self.head.lemma} {self.head.particle_token.text} {self.text}"
        )
        return potential_prt_prep_pv in PHRASAL_VERBS

    def _is_on_list_of_phrasal_verbs_with_preposition(self) -> bool:
        if self.head.is_phrasal_base_verb() and self.head.particle_token is not None:
            return self._is_on_list_of_phrasal_verbs_with_particle_and_preposition()
        potential_prep_pv = f"{self.head.lemma} {self.text}"
        return potential_prep_pv in PHRASAL_VERBS

    def _comes_right_after_verb_or_particle(self) -> bool:
        if self.head.is_phrasal_base_verb() and self.head.particle_token is not None:
            return self.i == self.head.particle_token.i + 1
        return self.i == self.head.i + 1

    def is_phrasal_verb_particle(self) -> bool:
        return self.dep == "prt" and self.head.pos == UNIVERSAL_POS_VERB

    def is_phrasal_verb_preposition(self) -> bool:
        return (
            self.dep == "prep"
            and self.head.pos == UNIVERSAL_POS_VERB
            and self._is_on_list_of_phrasal_verbs_with_preposition()
            and self._comes_right_after_verb_or_particle()
        )

    def is_phrasal_verb_prt_or_prep(self) -> bool:
        return self.is_phrasal_verb_particle() or self.is_phrasal_verb_preposition()

    def was_phrasal_verb_flagging_run(self) -> bool:
        return self._is_phrasal_verb_base_verb is not None

    def is_phrasal_base_verb(self) -> bool:
        if not self.was_phrasal_verb_flagging_run():
            raise PhrasalVerbError("Phrasal verb flagging not run")
        return self._is_phrasal_verb_base_verb  # type: ignore

    @property
    def particle_token(self) -> TokenEN:
        if not self.is_phrasal_base_verb():
            raise PhrasalVerbError("Not a phrasal base verb")
        return self._phrasal_verb_particle_token  # type: ignore

    @property
    def preposition_token(self) -> TokenEN:
        if not self.is_phrasal_base_verb():
            raise PhrasalVerbError("Not a phrasal base verb")
        return self._phrasal_verb_preposition_token  # type: ignore

    def flag_as_phrasal_base_verb(
        self,
        particle_token: Optional[TokenEN] = None,
        preposition_token: Optional[TokenEN] = None,
    ) -> None:
        self._is_phrasal_verb_base_verb = True

        if particle_token is None and preposition_token is None:
            raise PhrasalVerbError(
                "At least one of particle/preposition tokens must be provided"
            )

        if particle_token is not None:
            self._phrasal_verb_particle_token = particle_token
        if preposition_token is not None:
            self._phrasal_verb_preposition_token = preposition_token

    def is_translatable(self) -> bool:
        return self.tag in TRANSLATABLE_EN_POS

    @property
    def pos_simple(self) -> str:
        """
        Raises KeyError if the word doesn't have a simple POS.
        Run this method if is_translatable() == True.
        """
        return LEMMATIZABLE_EN_POS_TO_POS_SIMPLE[self.tag]

    def _phrasal_verb_str(self, use_lemma=False) -> str:
        result = self.lemma if use_lemma else self.text
        if self.particle_token is not None:
            result += f" {self.particle_token.text}"
        if self.preposition_token is not None:
            result += f" {self.preposition_token.text}"
        return result

    def _word_extended(self, use_lemma=False) -> str:
        word = self.lemma if use_lemma else self.text
        if not self.was_phrasal_verb_flagging_run():
            return word
        if self.is_phrasal_base_verb():
            return self._phrasal_verb_str(use_lemma=use_lemma)
        return word

    @property
    def lemma_extended(self) -> str:
        return self._word_extended(use_lemma=True)

    @property
    def text_extended(self) -> str:
        return self._word_extended(use_lemma=False)
