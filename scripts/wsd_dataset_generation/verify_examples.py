import argparse
import csv
import re
from typing import Any, Literal

from chatgpt import get_single_response_from_chat_gpt
from constants import (
    VERIFICATION_KEYS,
    WORDNET_POS__TO__HUMAN_READABLE_POS,
    WORDNET_POS__TO__LEMMATIZATION_POS,
)
from lemmatization import LemmatizedSentence, lemmatize_sentence
from nltk.corpus import wordnet as wn
from run_esr import MODEL_NAME_BASE, MODEL_NAME_LARGE, disambiguate_sentence

CheckResult = Literal["Correct", "Incorrect", "Error", "Not tried"]

OUTPUT_PATH = "new_sentences_verified.csv"

INPUT_HEADER = (
    "index|lemma|human_readable_pos|definition|synset_key_name|example|new_sentence"
)

OUTPUT_HEADER = INPUT_HEADER + "|" + "|".join(VERIFICATION_KEYS) + "\n"

NOT_TRIED = "Not tried"


def is_correct_example_using_esr(
    lemmatized_sentence: LemmatizedSentence,
    lemma: str,
    expected_synset: wn.synset,
    model_name: str,
) -> tuple[CheckResult, float, float]:
    try:
        wsd_result = disambiguate_sentence(
            lemmatized_sentence, lemma, expected_synset.pos(), 0, model_name
        )
    except:
        return "Error", 0.0, 0.0
    if wsd_result.top_synset == expected_synset:
        correct_or_incorrect = "Correct"
    else:
        correct_or_incorrect = "Incorrect"
    esr_score_for_expected_synset = wsd_result.synset__to__score[expected_synset]
    highest_synset_score = wsd_result.synset__to__score[wsd_result.top_synset]
    return correct_or_incorrect, esr_score_for_expected_synset, highest_synset_score


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
    lemmatized_sentence: LemmatizedSentence, lemma: str, wn_pos: str
) -> CheckResult:
    if (
        sum(
            map(
                lambda x: lemma == x[1]
                and WORDNET_POS__TO__LEMMATIZATION_POS[wn_pos] == x[2],
                lemmatized_sentence,
            )
        )
        == 1
    ):
        return "Correct"
    return "Incorrect"


def verify_example(generated_example: dict) -> dict[str, CheckResult]:
    result = {
        verification_key: generated_example.get(verification_key, "Not tried")
        for verification_key in VERIFICATION_KEYS
    }

    generated_sentence = generated_example["new_sentence"]
    lemma = generated_example["lemma"]
    expected_synset = wn.synset(generated_example["synset_key_name"])

    lemmatized_sentence = lemmatize_sentence(generated_sentence)
    if (
        example_actually_contains_exactly_one_lemma(
            lemmatized_sentence, lemma, expected_synset.pos()
        )
        == "Incorrect"
    ):
        if result["v__contains_lemma"] == "Correct":
            print(f"Other decision of contains_lemma for {generated_example['index']}")
        return {**{key: NOT_TRIED for key in result}, "v__contains_lemma": "Incorrect"}

    if not any(result_value == NOT_TRIED for result_value in result.values()):
        return result

    result["v__contains_lemma"] = "Correct"

    if NOT_TRIED in [
        result["v__esr_base"],
        result["v__esr_base_score"],
        result["v__esr_base_highest_score"],
    ]:
        (
            correct_or_incorrect_esr_base,
            esr_base_score,
            highest_esr_base_score,
        ) = is_correct_example_using_esr(
            lemmatized_sentence, lemma, expected_synset, MODEL_NAME_BASE
        )
        result["v__esr_base"] = correct_or_incorrect_esr_base
        result["v__esr_base_score"] = esr_base_score
        result["v__esr_base_highest_score"] = highest_esr_base_score

    if NOT_TRIED in [
        result["v__esr_large"],
        result["v__esr_large_score"],
        result["v__esr_large_highest_score"],
    ]:
        (
            correct_or_incorrect_esr_large,
            esr_large_score,
            highest_esr_large_score,
        ) = is_correct_example_using_esr(
            lemmatized_sentence, lemma, expected_synset, MODEL_NAME_LARGE
        )
        result["v__esr_large"] = correct_or_incorrect_esr_large
        result["v__esr_large_score"] = esr_large_score
        result["v__esr_large_highest_score"] = highest_esr_large_score

    if result["v__gpt35__disambiguate"] == NOT_TRIED:
        result["v__gpt35__disambiguate"] = verify_with_gpt__disambiguate(
            generated_sentence, lemma, expected_synset
        )
    if result["v__gpt35__verify"] == NOT_TRIED:
        result["v__gpt35__verify"] = verify_with_gpt__yes_or_no(
            generated_sentence, lemma, expected_synset
        )

    if result["v__number_of_possible_synsets"] == NOT_TRIED:
        result["v__number_of_possible_synsets"] = len(
            wn.synsets(lemma=lemma, pos=expected_synset.pos())
        )

    result["v__number_of_successes"] = sum(
        map(
            lambda x: x == "Correct",
            [
                result[key]
                for key in [
                    "v__esr_base",
                    "v__esr_large",
                    "v__gpt35__verify",
                    "v__gpt35__disambiguate",
                ]
            ],
        )
    )

    return result


def load_input(input_path: str) -> list[dict[str, Any]]:
    with open(input_path, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return list(reader)


def create_output_if_doesnt_exist(output_path: str) -> None:
    try:
        with open(output_path, "r", encoding="utf_8") as f:
            if f.readline() != OUTPUT_HEADER:
                raise FileNotFoundError(f"Output file {output_path} incorrect")
    except FileNotFoundError:
        with open(output_path, "w", encoding="utf_8") as f:
            f.write(OUTPUT_HEADER)


def verify_examples(input_path: str, output_path: str, start_from_index: int) -> None:
    generated_examples = load_input(input_path)
    create_output_if_doesnt_exist(output_path)
    number_of_esr_errors = 0
    with open(output_path, "a", encoding="utf_8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[header.strip() for header in OUTPUT_HEADER.split("|")],
            delimiter="|",
        )
        for generated_example in generated_examples:
            if int(generated_example["index"]) < start_from_index:
                continue
            verification = verify_example(generated_example)
            if "Error" in [verification["v__esr_base"], verification["v__esr_large"]]:
                number_of_esr_errors += 1
            if number_of_esr_errors > 20:
                raise ValueError
            result = {
                **generated_example,
                **verification,
            }
            if "" in result:
                del result[""]
            writer.writerow(result)
            csvfile.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=False, default=OUTPUT_PATH)
    parser.add_argument("--start_from_index", type=int, required=False, default=0)
    args = parser.parse_args()
    verify_examples(args.input, args.output, args.start_from_index)
