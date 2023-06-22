import backoff
import openai


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def get_single_response_from_chat_gpt(
    gpt_prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 1,
    system_message: str = "You are a helpful assistant.",
) -> str:
    return openai.ChatCompletion.create(
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
