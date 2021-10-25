import dataclasses
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, root_validator

from smart_word_hints_api.app.constants import EN
from smart_word_hints_api.app.hints_providers import EnglishToEnglishHintsProvider

VALID_LANG_PAIRS = [(EN, EN)]

app = FastAPI(
    title="Smart Word Hints",
    description="API for the browser extension displaying hints above difficult words",
    version="0.0.1",
)


class HintsOptions(BaseModel):
    text_language: Optional[str] = EN
    hints_language: Optional[str] = EN
    difficulty: Optional[int] = Field(
        default=1000,
        description="Only show hints for words less common than this number",
        ge=0,
    )

    @root_validator
    def are_valid_languages(cls, values):
        text_lang = values["text_language"]
        hints_lang = values["hints_language"]
        if (text_lang, hints_lang) not in VALID_LANG_PAIRS:
            raise ValueError(f"Currently supported language pairs: {VALID_LANG_PAIRS}")
        return values


class WordHintsRequest(BaseModel):
    text: str
    options: Optional[HintsOptions] = HintsOptions()


en_to_en_hints_provider = EnglishToEnglishHintsProvider()


@app.post("/api/get_hints")
def get_hints(request_body: WordHintsRequest):
    hints = en_to_en_hints_provider.get_hints(
        request_body.text, request_body.options.difficulty
    )
    return {"hints": [dataclasses.asdict(hint) for hint in hints]}


@app.get("/api/available_languages")
def available_languages():
    return VALID_LANG_PAIRS


@app.get("/")
def main_get():
    return RedirectResponse(url="/docs")
