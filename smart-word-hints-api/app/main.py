from typing import Optional, List, Tuple

from nltk import FreqDist, tokenize
from nltk.corpus import brown, wordnet
from fastapi import FastAPI
from pydantic import BaseModel, Field, validator

VALID_LANG_CODES = ["en"]

app = FastAPI()


class HintsOptions(BaseModel):
    text_language: Optional[str] = "en"
    hints_language: Optional[str] = "en"
    difficulty: Optional[int] = Field(
        default=1000,
        description="Only show hints for words less common than this number",
        ge=0,
    )

    @validator("text_language", "hints_language")
    def is_valid_lang_code(cls, lang_code):
        if lang_code not in VALID_LANG_CODES:
            raise ValueError(f"Currently supported languages: {VALID_LANG_CODES}")
        return lang_code


class WordHintsRequest(BaseModel):
    text: str
    options: Optional[HintsOptions] = HintsOptions()


words_freq_brown: FreqDist = FreqDist(brown.words())
words_ranking: List[str] = [
    freq[0] for freq in words_freq_brown.most_common(len(words_freq_brown))
]


def get_tokens_with_spans(text: str) -> List[Tuple[int, int]]:
    tokens = tokenize.word_tokenize(text)
    offset = 0
    for token in tokens:
        offset = text.find(token, offset)
        yield token, offset, offset + len(token)
        offset += len(token)


def get_hint(word: str, start: int, end: int) -> Optional[dict]:
    try:
        definition = wordnet.synsets(word)[0].definition()
    except IndexError:
        return None

    try:
        ranking = words_ranking.index(word)
    except ValueError:
        ranking = None

    return {
        "word": word,
        "start": start,
        "end": end,
        "ranking": ranking,
        "definition": definition,
    }


@app.post("/api/get_hints")
def get_hints(request_body: WordHintsRequest):
    most_common = words_ranking[: request_body.options.difficulty]
    hints = []
    tokens_with_spans = list(get_tokens_with_spans(request_body.text))
    for word, start, end in tokens_with_spans:
        if word not in most_common:
            hint = get_hint(word, start, end)
            if hint is not None:
                hints.append(hint)
    return {"hints": hints}
