import csv
from typing import Any

from chatgpt import get_single_response_from_chat_gpt

INPUT_PATH = "input_data_sentences_to_generate.csv"
OUTPUT_PATH = "new_sentences.csv"
OUTPUT_HEADER = (
    "index|lemma|human_readable_pos|definition|synset_key_name|example|new_sentence\n"
)
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


def get_already_generated() -> set[str]:
    with open(OUTPUT_PATH, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return set([row["index"] for row in reader])


def generate_sentences():
    create_output_if_doesnt_exist()
    already_generated = get_already_generated()
    with open(OUTPUT_PATH, "a", encoding="utf_8") as f:
        output_writer = csv.writer(f, delimiter="|")
        for sentence_to_generate_data in load_input():
            if sentence_to_generate_data["index"] in already_generated:
                continue
            lemma = sentence_to_generate_data["lemma"]
            pos = sentence_to_generate_data["human_readable_pos"]
            prompt = GPT_PROMPT_TEMPLATE.format(
                pos="phrasal verb" if "_" in lemma and pos == "verb" else pos,
                lemma=lemma.replace("_", " "),
                definition=sentence_to_generate_data["definition"],
                example=sentence_to_generate_data["example"],
            )
            new_sentence = get_single_response_from_chat_gpt(prompt, temperature=1.5)
            output_writer.writerow(
                [
                    sentence_to_generate_data["index"],
                    sentence_to_generate_data["lemma"],
                    sentence_to_generate_data["human_readable_pos"],
                    sentence_to_generate_data["definition"],
                    # fixing incorrect serialization in input
                    sentence_to_generate_data["synset_key_name"][
                        len("Synset('") : -len("')")
                    ],
                    sentence_to_generate_data["example"],
                    new_sentence,
                ]
            )
            already_generated.add(sentence_to_generate_data["index"])
            f.flush()


if __name__ == "__main__":
    generate_sentences()
