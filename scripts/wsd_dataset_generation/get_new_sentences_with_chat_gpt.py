import csv
from typing import Any

import backoff
import openai

INPUT_PATH = "input_data_sentences_to_generate.csv"
OUTPUT_PATH = "new_sentences.csv"
OUTPUT_HEADER = "lemma|pos|definition|synset_key_name|example|new_sentence\n"
GPT_PROMPT_TEMPLATE = """{pos} "{lemma}" can mean, among others: {definition}. 
Example sentence: {example} 
Write a different example sith {pos} "{lemma}" with exactly this meaning:
"""


def load_input() -> list[dict[str, Any]]:
    with open(INPUT_PATH, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return list(reader)


def create_output_if_doesnt_exist() -> None:
    try:
        with open(OUTPUT_PATH, "r", encoding="utf_8") as f:
            if f.readline() != OUTPUT_HEADER:
                raise FileNotFoundError(f"Output file {OUTPUT_PATH} incorrect")
    except FileNotFoundError:
        with open(OUTPUT_PATH, "w", encoding="utf_8") as f:
            f.write(OUTPUT_HEADER)


def get_synsets_for_which_already_generated() -> set[str]:
    with open(OUTPUT_PATH, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return set([row["synset_key_name"] for row in reader])


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def generate_sentence_with_chat_gpt(gpt_prompt: str) -> str:
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that generates correct sentences.",
            },
            {"role": "user", "content": gpt_prompt},
        ],
        temperature=0.5,
        max_tokens=256,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )["choices"][0]["message"]["content"]


def generate_sentences():
    create_output_if_doesnt_exist()
    synsets_already_generated = get_synsets_for_which_already_generated()
    with open(OUTPUT_PATH, "a", encoding="utf_8") as f:
        output_writer = csv.writer(f, delimiter="|")
        for sentence_to_generate_data in load_input():
            if (
                sentence_to_generate_data["synset_key_name"]
                in synsets_already_generated
            ):
                continue
            prompt = GPT_PROMPT_TEMPLATE.format(
                pos=sentence_to_generate_data["pos"],
                lemma=sentence_to_generate_data["lemma"],
                definition=sentence_to_generate_data["definition"],
                example=sentence_to_generate_data["example"],
            )
            new_sentence = generate_sentence_with_chat_gpt(prompt)
            output_writer.writerow(
                [
                    sentence_to_generate_data["lemma"],
                    sentence_to_generate_data["pos"],
                    sentence_to_generate_data["definition"],
                    sentence_to_generate_data["synset_key_name"],
                    sentence_to_generate_data["example"],
                    new_sentence,
                ]
            )
            synsets_already_generated.add(sentence_to_generate_data["synset_key_name"])
            f.flush()


if __name__ == "__main__":
    generate_sentences()
