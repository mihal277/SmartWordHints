import argparse
import csv
from itertools import groupby
from random import shuffle
from typing import Any

from nltk.corpus import wordnet as wn


def load_input(input_path: str) -> list[dict[str, Any]]:
    with open(input_path, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return list(reader)


def get_already_verified(output_path: str) -> set[str]:
    with open(output_path, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return set([row["index"] for row in reader])


def verify_as_human(
    input_path: str,
    output_path: str,
    number_of_sentences: int,
    prefer_least_certain: bool,
) -> None:
    input_data = load_input(input_path)
    already_done = get_already_verified(output_path)
    input_data_only_not_done = list(
        filter(lambda x: x["index"] not in already_done, input_data)
    )
    input_data_grouped = {
        key: list(val)
        for key, val in groupby(
            input_data_only_not_done,
            key=lambda x: (x["lemma"], x["human_readable_pos"]),
        )
    }
    verification_field_name = "v__human"
    with open(output_path, "a", encoding="utf_8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[*input_data_only_not_done[0].keys(), verification_field_name],
            delimiter="|",
        )
        if len(already_done) == 0:
            writer.writeheader()
        number_done = 0
        number_of_sentences_to_verify = number_of_sentences - len(already_done)

        lemma_pos_group_keys = list(input_data_grouped.keys())
        shuffle(lemma_pos_group_keys)

        while number_done < number_of_sentences_to_verify:
            for lemma_pos in lemma_pos_group_keys:
                sentences_data = input_data_grouped[lemma_pos]
                if prefer_least_certain:
                    sentences_data.sort(
                        key=lambda x: (x["v__esr_base_score"], x["v__esr_large_score"])
                    )
                else:
                    shuffle(sentences_data)
                for sentence_data in sentences_data:
                    if sentence_data["index"] in already_done:
                        continue
                    if sentence_data["v__contains_lemma"] == "Incorrect":
                        continue

                    print(sentence_data["lemma"])
                    print(sentence_data["human_readable_pos"])
                    print(sentence_data["definition"])
                    print(f"gold: {sentence_data['example']}")
                    print(f"generated: {sentence_data['new_sentence']}")
                    print("")

                    verification = None
                    while verification not in ["y", "n", "s"]:
                        verification = input("y/n/?/s: ")
                        if verification == "?":
                            synsets = wn.synsets(
                                lemma=sentence_data["lemma"],
                                pos=wn.synset(sentence_data["synset_key_name"]).pos(),
                            )
                            for i, synset in enumerate(synsets):
                                print(f"{i}: {synset.definition()}")
                                if synset.examples():
                                    print(f"  {'; '.join(synset.examples())}")

                    already_done.add(sentence_data["index"])

                    if verification == "s":
                        print("SKIPPING")
                        continue

                    number_done += 1
                    writer.writerow(
                        {
                            **sentence_data,
                            verification_field_name: 1 if verification == "y" else 0,
                        }
                    )
                    csvfile.flush()

                    print()
                    # go to next (lemma, pos) group
                    break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--number_of_sentences", type=int, required=True)
    parser.add_argument(
        "--prefer_least_certain",
        action=argparse.BooleanOptionalAction,
        required=False,
        default=False,
    )
    args = parser.parse_args()
    verify_as_human(
        args.input, args.output, args.number_of_sentences, args.prefer_least_certain
    )
