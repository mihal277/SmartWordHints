import argparse
import csv
from random import shuffle
from typing import Any


def load_input(input_path: str) -> list[dict[str, Any]]:
    with open(input_path, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return list(reader)


def get_already_verified(output_path: str) -> set[str]:
    with open(output_path, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        return set([row["index"] for row in reader])


def verify_as_human(
    input_path: str, output_path: str, number_of_sentences: int
) -> None:
    input_data = load_input(input_path)
    already_done = get_already_verified(output_path)
    input_data_only_not_done = list(
        filter(lambda x: x["index"] not in already_done, input_data)
    )
    shuffle(input_data_only_not_done)
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
        for sentence_data in input_data_only_not_done:
            if number_done >= number_of_sentences_to_verify:
                break

            print(sentence_data["lemma"])
            print(sentence_data["human_readable_pos"])
            print(sentence_data["definition"])
            print(f"gold: {sentence_data['example']}")
            print(f"generated: {sentence_data['new_sentence']}")
            print("")

            verification = None
            while verification not in ["y", "n", "?"]:
                verification = input("y/n/?: ")
            if verification == "?":
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--number_of_sentences", type=int, required=True)
    args = parser.parse_args()
    verify_as_human(args.input, args.output, args.number_of_sentences)
