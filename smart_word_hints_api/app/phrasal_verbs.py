from smart_word_hints_api.app.constants import EN_PHRASAL_VERBS_PATH


def load_phrasal_verbs() -> set[str]:
    with open(EN_PHRASAL_VERBS_PATH, "r") as f:
        return set(f.read().splitlines())
