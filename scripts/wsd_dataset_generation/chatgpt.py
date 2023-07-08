import logging

import backoff
from openai import ChatCompletion
from openai.error import (
    APIConnectionError,
    APIError,
    ServiceUnavailableError,
    Timeout,
    TryAgain,
)

logging.getLogger("backoff").addHandler(logging.StreamHandler())


@backoff.on_exception(
    backoff.expo,
    (APIError, TryAgain, Timeout, ServiceUnavailableError, APIConnectionError),
)
def get_single_response_from_chat_gpt(
    gpt_prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 1,
    system_message: str = "You are a helpful assistant.",
) -> str:
    return ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": gpt_prompt},
        ],
        temperature=temperature,
        max_tokens=256,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )["choices"][0]["message"]["content"]
