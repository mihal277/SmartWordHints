from nltk.corpus import wordnet as wn

RAW_LIST_PATH = ""
CLEAN_LIST_PATH = ""


def has_definition(raw_phrasal_verb: str) -> bool:
    return len(wn.synsets(raw_phrasal_verb.replace(" ", "_"))) > 0


def load_word_list() -> list[str]:
    with open(RAW_LIST_PATH, "r") as f:
        return f.read().splitlines()


def dump_word_list(word_list: list[str]) -> None:
    with open(CLEAN_LIST_PATH, "w") as f:
        for item in word_list:
            f.write(f"{item}\n")


def filter_out_phrasal_verbs_with_no_definition(phrasal_verbs: list[str]) -> list[str]:
    return list(filter(has_definition, phrasal_verbs))


if __name__ == "__main__":
    dump_word_list(filter_out_phrasal_verbs_with_no_definition(load_word_list()))
