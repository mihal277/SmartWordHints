import re
from typing import Literal

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

CheckResult = Literal["Correct", "Incorrect", "NA"]


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
        model="gpt-4",
        system_message="You are an assistant that responses with a number.",
    )
    print(chat_gpt_response)
    matches = re.findall(r"\d+", chat_gpt_response)
    if len(matches) != 1:
        return "NA"

    if len(matches) == 1:
        chosen_definition_index = int(matches[0])
        if chosen_definition_index == expected_synset_index:
            return "Correct"
        return "Incorrect"
    else:
        return "NA"


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
        model="gpt-4",
        system_message="You are an assistant that responses either Yes or No.",
    ).lower()

    print(chat_gpt_response)
    if "yes" in chat_gpt_response and "no" not in chat_gpt_response:
        return "Correct"
    if "no" in chat_gpt_response and "yes" not in chat_gpt_response:
        return "Incorrect"
    return "NA"


def example_actually_contains_exactly_one_lemma(
    lemmatized_sentence: LemmatizedSentence, lemma: str
) -> CheckResult:
    if sum(map(lambda x: lemma == x[1], lemmatized_sentence)) == 1:
        return "Correct"
    return "Incorrect"


def verify_example(
    sentence: str, lemma: str, expected_synset: wn.synset
) -> dict[str, CheckResult]:
    lemmatized_sentence = lemmatize_sentence(sentence)
    if not example_actually_contains_exactly_one_lemma(lemmatized_sentence, lemma):
        return {"contains_lemma": "Incorrect"}

    return {
        "contains_lemma": "Correct",
        "is_correct_using_esr_base": is_correct_example_using_esr(
            lemmatized_sentence, lemma, expected_synset, MODEL_NAME_BASE
        ),
        "is_correct_using_esr_large": is_correct_example_using_esr(
            lemmatized_sentence, lemma, expected_synset, MODEL_NAME_LARGE
        ),
        "is_correct_using_chat_gpt__asking_to_disambiguate": verify_with_gpt__disambiguate(
            sentence, lemma, expected_synset
        ),
        "is_correct_using_chat_gpt__asking_to_verify_meaning": verify_with_gpt__yes_or_no(
            sentence, lemma, expected_synset
        ),
    }
