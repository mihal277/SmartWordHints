from __future__ import annotations

import functools

import spacy

from smart_word_hints_api.app.constants import UNIVERSAL_POS_VERB
from smart_word_hints_api.app.token_wrappers import TokenEN

nlp_en = spacy.load("en_core_web_sm")


class TextHolderEN:
    def __init__(self, text: str, flag_phrasal_verbs: bool = False):
        self.raw_text = text
        self.doc = nlp_en(text)
        if flag_phrasal_verbs:
            self.flag_phrasal_verb_base_verbs()

    @functools.cached_property
    def tokens(self) -> list[TokenEN]:
        result = []
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
        return result

    def _tag_all_tokens_as_non_phrasal_verb_base(self) -> None:
        for token in self.tokens:
            token._is_phrasal_verb_base_verb = False

    def flag_phrasal_verb_base_verbs(self) -> None:
        self._tag_all_tokens_as_non_phrasal_verb_base()
        particle_tokens = set()
        for token in reversed(self.tokens):
            if token.is_phrasal_verb_particle():
                particle_tokens.add(token)
            elif token.pos == UNIVERSAL_POS_VERB:
                for particle_occurring_later in particle_tokens:
                    if particle_occurring_later.head.text == token.text:
                        token.flag_as_phrasal_base_verb(particle_occurring_later)
                        particle_tokens.remove(particle_occurring_later)
                        break
