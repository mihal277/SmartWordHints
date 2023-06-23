import csv
import re
from typing import Any, Literal

from chatgpt import get_single_response_from_chat_gpt
from lemmatization import LemmatizedSentence, lemmatize_sentence
from nltk.corpus import wordnet as wn
from run_esr import MODEL_NAME_BASE, MODEL_NAME_LARGE, disambiguate_sentence

WORDNET_POS__TO__HUMAN_READABLE_POS = {
    wn.ADJ: "adjective",
    wn.ADJ_SAT: "adjective",
    wn.ADV: "adverb",
    wn.NOUN: "noun",
    wn.VERB: "verb",
}

CheckResult = Literal["Correct", "Incorrect", "Error", "Not tried"]

INPUT_PATH = "new_sentences.csv"
OUTPUT_PATH = "new_sentences_verified.csv"

INPUT_HEADER = (
    "index|lemma|human_readable_pos|definition|synset_key_name|example|new_sentence\n"
)
OUTPUT_HEADER = (
    "index|lemma|human_readable_pos|definition|synset_key_name|example|new_sentence|"
    "v__contains_lemma|"
    "v__esr_base|"
    "v__esr_large|"
    "v__gpt35__disambiguate|"
    "v__gpt35__verify|"
    "v__number_of_successes|\n"
)


def is_correct_example_using_esr(
    lemmatized_sentence: LemmatizedSentence,
    lemma: str,
    expected_synset: wn.synset,
    model_name: str,
) -> CheckResult:
    if (
        disambiguate_sentence(lemmatized_sentence, lemma, 0, model_name)
        == expected_synset
    ):
        return "Correct"
    return "Incorrect"


def verify_with_gpt__disambiguate(
    sentence: str, lemma: str, expected_synset: wn.synset
) -> CheckResult:
    pos = expected_synset.pos()
    human_readable_pos = WORDNET_POS__TO__HUMAN_READABLE_POS[pos]
    prompt = f'The {human_readable_pos} "{lemma}" can have the following meanings:\n'
    expected_synset_index = None
    for i, possible_synset_for_lemma in enumerate(wn.synsets(lemma, pos), start=1):
        if possible_synset_for_lemma == expected_synset:
            expected_synset_index = i
        prompt += f"{i}. {possible_synset_for_lemma.definition()}\n"
    assert expected_synset_index is not None
    prompt += (
        f"Here's an example sentence:\n"
        f"{sentence}\n"
        f"Which of the meanings does the sentence use? Answer with number."
    )
    chat_gpt_response = get_single_response_from_chat_gpt(
        gpt_prompt=prompt,
        model="gpt-3.5-turbo",
        system_message="You are an assistant that replies with a number.",
        temperature=0,
    )
    matches = re.findall(r"\d+", chat_gpt_response)
    if len(matches) != 1:
        return "Error"

    if len(matches) == 1:
        chosen_definition_index = int(matches[0])
        if chosen_definition_index == expected_synset_index:
            return "Correct"
        return "Incorrect"
    else:
        return "Error"


def verify_with_gpt__yes_or_no(
    sentence: str, lemma: str, expected_synset: wn.synset
) -> CheckResult:
    human_readable_pos = WORDNET_POS__TO__HUMAN_READABLE_POS[expected_synset.pos()]
    prompt = (
        f"Here's an example sentence:\n"
        f'"{sentence}"\n'
        f'Does the {human_readable_pos} "{lemma}" in this sentence'
        f'have the sense "{expected_synset.definition()}"? Answer Yes/No.'
    )
    chat_gpt_response = get_single_response_from_chat_gpt(
        gpt_prompt=prompt,
        model="gpt-3.5-turbo",
        system_message="You are an assistant that responses either Yes or No.",
    ).lower()

    if "yes" in chat_gpt_response and "no" not in chat_gpt_response:
        return "Correct"
    if "no" in chat_gpt_response and "yes" not in chat_gpt_response:
        return "Incorrect"
    return "Error"


def example_actually_contains_exactly_one_lemma(
    lemmatized_sentence: LemmatizedSentence, lemma: str
) -> CheckResult:
    if sum(map(lambda x: lemma == x[1], lemmatized_sentence)) == 1:
        return "Correct"
    return "Incorrect"


def verify_example(
    sentence: str, lemma: str, expected_synset: wn.synset
) -> dict[str, CheckResult]:
    result = {
        "v__contains_lemma": "Not tried",
        "v__esr_base": "Not tried",
        "v__esr_large": "Not tried",
        "v__gpt35__disambiguate": "Not tried",
        "v__gpt35__verify": "Not tried",
    }

    lemmatized_sentence = lemmatize_sentence(sentence)
    if (
        example_actually_contains_exactly_one_lemma(lemmatized_sentence, lemma)
        == "Incorrect"
    ):
        result["v__contains_lemma"] = "Incorrect"
        return result

    result["v__contains_lemma"] = "Correct"
    result["v__esr_base"] = is_correct_example_using_esr(
        lemmatized_sentence, lemma, expected_synset, MODEL_NAME_BASE
    )
    result["v__esr_large"] = is_correct_example_using_esr(
        lemmatized_sentence, lemma, expected_synset, MODEL_NAME_LARGE
    )
    result["v__gpt35__disambiguate"] = verify_with_gpt__disambiguate(
        sentence, lemma, expected_synset
    )
    result["v__gpt35__verify"] = verify_with_gpt__yes_or_no(
        sentence, lemma, expected_synset
    )
    return result


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


def get_already_verified() -> set[str]:
    with open(OUTPUT_PATH, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return set([row["index"] for row in reader])


def verify_examples():
    generated_examples = load_input()
    create_output_if_doesnt_exist()
    already_verified = get_already_verified()
    with open(OUTPUT_PATH, "a", encoding="utf_8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[header.strip() for header in OUTPUT_HEADER.split("|")],
            delimiter="|",
        )
        for generated_example in generated_examples:
            if generated_example["index"] in already_verified:
                continue
            verification = verify_example(
                generated_example["new_sentence"],
                generated_example["lemma"],
                wn.synset(generated_example["synset_key_name"]),
            )
            number_of_successes = sum(
                map(lambda x: x == "Correct", verification.values())
            )
            result = {
                **generated_example,
                **verification,
                "v__number_of_successes": number_of_successes,
            }
            writer.writerow(result)
            already_verified.add(generated_example["index"])
            csvfile.flush()


if __name__ == "__main__":
    verify_examples()
