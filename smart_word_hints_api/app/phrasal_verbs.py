from pathlib import Path

from smart_word_hints_api.app.constants import EN_PHRASAL_VERBS_RELATIVE_PATH


def load_phrasal_verbs() -> set[str]:
    phrasal_verbs_path = Path(__file__).parent / EN_PHRASAL_VERBS_RELATIVE_PATH
    with open(phrasal_verbs_path, "r") as f:
        return set(f.read().splitlines())
