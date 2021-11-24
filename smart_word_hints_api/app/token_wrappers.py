from __future__ import annotations

from typing import Optional

from spacy.tokens.token import Token

from smart_word_hints_api.app.constants import (
    LEMMATIZABLE_EN_POS_TO_POS_SIMPLE,
    TRANSLATABLE_EN_POS,
    UNIVERSAL_POS_VERB,
)
from smart_word_hints_api.app.difficulty_rankings import DifficultyRankingEN

difficulty_ranking_en = DifficultyRankingEN()


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
    def head(self) -> Token:
        return self.raw_token.head


class PhrasalVerbError(Exception):
    pass


class TokenEN(TokenWrapper):
    def __init__(self, spacy_token: Token, start_position: int, end_position: int):
        super().__init__(spacy_token, start_position, end_position)
        self._is_phrasal_verb_base_verb: Optional[bool] = None
        self._phrasal_verb_particle_token: Optional[TokenEN] = None

    def is_phrasal_verb_particle(self) -> bool:
        return self.dep in "prt" and self.head.pos_ == UNIVERSAL_POS_VERB

    def is_phrasal_base_verb(self) -> bool:
        if self._is_phrasal_verb_base_verb is None:
            raise PhrasalVerbError("Phrasal verb flagging not run")
        return self._is_phrasal_verb_base_verb

    @property
    def particle_token(self) -> TokenEN:
        if not self.is_phrasal_base_verb():
            raise Exception("Not a phrasal base verb")
        return self._phrasal_verb_particle_token  # type: ignore

    def flag_as_phrasal_base_verb(self, particle_token: TokenEN) -> None:
        self._is_phrasal_verb_base_verb = True
        self._phrasal_verb_particle_token = particle_token

    def is_translatable(self) -> bool:
        return self.tag in TRANSLATABLE_EN_POS

    @property
    def pos_simple(self) -> str:
        """
        Raises KeyError if the word doesn't have a simple POS.
        Run this method if is_translatable() == True.
        """
        return LEMMATIZABLE_EN_POS_TO_POS_SIMPLE[self.tag]
