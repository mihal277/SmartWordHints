import csv

from sklearn.metrics import f1_score, fbeta_score


def load_human_verification() -> dict[int, int]:
    hv = {}
    with open(
        "new_sentences_verified_with_human_verification.csv",
        newline="",
        encoding="utf_8",
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        for row in list(reader):
            hv[int(row["index"])] = int(row["v__human"])

    return hv


def load_verify_attempt_by_gpt(path) -> dict[int, int]:
    attempt = {}
    with open(path, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        for d in list(reader):
            if "v__gpt35__disambiguate_v2" in d:
                attempt[int(d["index"])] = (
                    1 if d["v__gpt35__disambiguate_v2"] == "Correct" else 0
                )
            else:
                attempt[int(d["index"])] = (
                    1 if d["v__gpt35__disambiguate"] == "Correct" else 0
                )
    return attempt


def do(path):
    hv = load_human_verification()
    attempt = load_verify_attempt_by_gpt(path)

    correct = 0
    not_included = 0
    incorrect = 0

    for k, v in attempt.items():
        if k not in hv:
            not_included += 1
        elif hv[k] == v:
            correct += 1
        else:
            incorrect += 1

    values_hv = []
    values_attempt = []

    for k, v in attempt.items():
        if k not in hv:
            continue
        values_attempt.append(v)
        values_hv.append(hv[k])

    print(f"Correct {correct}")
    print(f"Incorrect {incorrect}")
    print(f"Included {correct+incorrect}")
    print(f"Not included {not_included}")
    print(f"Acc: {correct / (correct + incorrect)}")
    print(f"F1: {f1_score(values_hv, values_attempt)}")
    print(f"F05: {fbeta_score(values_hv, values_attempt, beta=0.5)}")
    print(f"F01: {fbeta_score(values_hv, values_attempt, beta=0.1)}")
    print(f"F00: {fbeta_score(values_hv, values_attempt, beta=0.0)}")


do("new_sentences_verified.csv")
print()
do("new_sentences_verified3.csv")
