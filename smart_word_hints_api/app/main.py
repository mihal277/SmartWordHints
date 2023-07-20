import dataclasses
from typing import Optional

import lambdawarmer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum
from pydantic import BaseModel, Field, root_validator

from smart_word_hints_api.app.config import config
from smart_word_hints_api.app.constants import CONFIG_KEY_LAMBDAWARMER_SEND_METRIC, EN
from smart_word_hints_api.app.hints_providers import EnglishToEnglishHintsProvider

VALID_LANG_PAIRS = [(EN, EN)]

MAJOR_VERSION = 1
MINOR_VERSION = 0
PATCH_VERSION = 0

app = FastAPI(
    title="Smart Word Hints",
    description="API for the browser extension displaying hints above difficult words",
    version=f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class HintsOptions(BaseModel):
    text_language: Optional[str] = EN
    hints_language: Optional[str] = EN
    avoid_repetitions: Optional[bool] = Field(
        default=True,
        description="Specifies if repeating the same hints should be avoided",
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


@app.post(f"/api/v{MAJOR_VERSION}/get_hints")
@app.post("/api/latest/get_hints")
def get_hints(request_body: WordHintsRequest):
    hints = en_to_en_hints_provider.get_hints(
        request_body.text,
        request_body.options.avoid_repetitions,  # type: ignore
    )
    return {"hints": [dataclasses.asdict(hint) for hint in hints]}


@app.get(f"/api/v{MAJOR_VERSION}/available_languages")
@app.get("/api/latest/available_languages")
def available_languages():
    return VALID_LANG_PAIRS


@app.get("/")
def main_get():
    return RedirectResponse(url="/docs")


mangum_handler = Mangum(app)


@lambdawarmer.warmer(send_metric=config.getboolean(CONFIG_KEY_LAMBDAWARMER_SEND_METRIC))
def lambda_handler(event, context):
    return mangum_handler(event, context)
