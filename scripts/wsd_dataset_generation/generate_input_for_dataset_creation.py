import csv
import math
import xml.etree.ElementTree as ET

from lemmatization import lemmatize_sentence
from nltk.corpus import wordnet as wn

SEMCOR_DATASET_PATH = (
    "esr/data/WSD_Evaluation_Framework/Training_Corpora/SemCor/semcor.data.xml"
)
SEMCOR_GOLD_PATH = (
    "esr/data/WSD_Evaluation_Framework/Training_Corpora/SemCor/semcor.gold.key.txt"
)
OUTPUT_PATH = "input_data_sentences_to_generate.csv"

SEMCOR_POS__TO__WN_POS = {
    "ADJ": wn.ADJ,
    "ADV": wn.ADV,
    "NOUN": wn.NOUN,
    "VERB": wn.VERB,
}

SEMCOR_POS__TO__HUMAN_READABLE_POS = {
    "ADJ": "adjective",
    "ADV": "adverb",
    "NOUN": "noun",
    "VERB": "verb",
}

MAJORITY_SENSE_DESIRED_MAX_CUTOFF = 0.652

MAX_SENTENCES_TO_GENERATE = 30


def create_sentence(word_list: list[str]) -> str:
    sentence = " ".join(word_list)
    sentence = sentence.replace(" '", "'")
    sentence = sentence.replace(" ,", ",")
    sentence = sentence.replace(" .", ".")
    sentence = sentence.replace(" ?", "?")
    sentence = sentence.replace(" !", "!")
    sentence = sentence.replace(" ;", ";")
    sentence = sentence.replace(" )", ")")
    sentence = sentence.replace("( ", "(")
    sentence = sentence.replace(" n't", "n't")
    sentence = sentence.replace(" - ", "-")
    sentence = sentence.replace("$ ", "$")
    sentence = sentence.strip()
    sentence = sentence.capitalize()
    return sentence


def sentence_contains_lemma(sentence: str, lemma: str) -> bool:
    # simple check that doesn't consider part of speech
    lemmatized_sentence = lemmatize_sentence(sentence)
    for word, lemma_, pos_ in lemmatized_sentence:
        if lemma_ == lemma:
            return True
    return False


def choose_example_sentence(
    semcor_examples: list[str], lemma: str, synset: wn.synset
) -> str:
    # preferably a short one u
    examples_from_wordnet = [
        example
        for example in synset.examples()
        if sentence_contains_lemma(example, lemma)
    ]
    return sorted(semcor_examples + examples_from_wordnet, key=lambda x: len(x))[0]


def get_example(
    lemma, pos, synset, lemma_pos_synset__to__instance_ids, sent_id_to_sentence
):
    instances_for_that_lemma_pos_synset = lemma_pos_synset__to__instance_ids[
        (lemma, pos, synset)
    ]

    semcor_examples = [
        sent_id_to_sentence[".".join(instance_for_that_lemma_pos_synset.split(".")[:2])]
        for instance_for_that_lemma_pos_synset in instances_for_that_lemma_pos_synset
    ]

    return choose_example_sentence(semcor_examples, lemma, synset)


def get_dataset_mappings():
    id_to_lemma = {}
    id_to_pos = {}
    id__to__lemma_pos_synsets = {}
    id_to_expected_synset_keys = {}
    id_to_expected_synsets = {}
    sent_id_to_sentence = {}
    lemma_pos__to__synset_count = {}
    lemma_pos_synset__to__instance_ids = {}

    with open(SEMCOR_GOLD_PATH, "r") as file:
        for line in file.readlines():
            line = line.split()
            id_to_expected_synset_keys[line[0]] = line[1:]
            id_to_expected_synsets[line[0]] = [
                wn.synset_from_sense_key(key) for key in line[1:]
            ]

    semcor_dataset_root = ET.parse(SEMCOR_DATASET_PATH).getroot()
    for element in semcor_dataset_root.iter():
        if element.tag == "instance":
            id_ = element.attrib["id"]
            id_to_lemma[id_] = element.attrib["lemma"]
            id_to_pos[id_] = element.attrib["pos"]

            id__to__lemma_pos_synsets.setdefault(id_, [])
            for synset in id_to_expected_synsets[id_]:
                val = (element.attrib["lemma"], element.attrib["pos"], synset)
                id__to__lemma_pos_synsets[id_].append(val)

    sentences = semcor_dataset_root.findall(".//sentence")
    for i, sentence in enumerate(sentences):
        sent_id = sentence.get("id")
        sentence_text = create_sentence([child.text for child in sentence])
        sent_id_to_sentence[sent_id] = sentence_text

    for id_, lemma in id_to_lemma.items():
        pos = id_to_pos[id_]
        lemma_pos = (lemma, pos)
        lemma_pos__to__synset_count.setdefault(lemma_pos, dict())
        synset_keys_for_lemma = id_to_expected_synset_keys[id_]
        for synset in wn.synsets(lemma, pos=SEMCOR_POS__TO__WN_POS[pos]):
            lemma_pos__to__synset_count[lemma_pos].setdefault(synset, 0)
        for synset_key in synset_keys_for_lemma:
            synset = wn.synset_from_sense_key(synset_key)
            lemma_pos__to__synset_count[lemma_pos][synset] += 1

    for instance_id, lemma_pos_synsets in id__to__lemma_pos_synsets.items():
        for lemma_pos_synset in lemma_pos_synsets:
            lemma_pos_synset__to__instance_ids.setdefault(lemma_pos_synset, [])
            lemma_pos_synset__to__instance_ids[lemma_pos_synset].append(instance_id)

    return (
        id_to_lemma,
        id_to_pos,
        id__to__lemma_pos_synsets,
        id_to_expected_synset_keys,
        id_to_expected_synsets,
        sent_id_to_sentence,
        lemma_pos__to__synset_count,
        lemma_pos_synset__to__instance_ids,
    )


def is_majority_sense_more_than(sense__to__count, cutoff):
    return max(sense__to__count.values()) / sum(sense__to__count.values()) > cutoff


def get_non_majority_senses_for_which_to_generate_examples_and_count(
    synset_counter: dict[wn.synset, int]
) -> tuple[set, int]:
    majority_sense_cnt = max(synset_counter.values())
    other_senses_cnt = sum(synset_counter.values()) - max(synset_counter.values())

    number_of_non_majority_sentences_to_generate = math.ceil(
        majority_sense_cnt * 0.534 - other_senses_cnt
    )

    senses_for_which_to_generate = {
        sense
        for sense, cnt in synset_counter.items()
        if cnt != majority_sense_cnt and cnt > 0  # don't generate if sense is very rare
    }
    assert len(senses_for_which_to_generate) > 0

    number_to_generate_for_each_sense = math.ceil(
        number_of_non_majority_sentences_to_generate / len(senses_for_which_to_generate)
    )

    number_to_generate = number_to_generate_for_each_sense * len(
        senses_for_which_to_generate
    )
    assert (
        sum(synset_counter.values()) + number_to_generate
    ) * MAJORITY_SENSE_DESIRED_MAX_CUTOFF >= majority_sense_cnt

    return senses_for_which_to_generate, min(
        MAX_SENTENCES_TO_GENERATE, number_to_generate_for_each_sense
    )


def get_lemma_pos__to__synset_count_to_generate(lemma_pos__to__existing_synset_count):
    lemma_pos__to__synset_count_to_generate = {}
    for lemma_pos, synset_counter in lemma_pos__to__existing_synset_count.items():
        majority_sense_cnt = max(synset_counter.values())
        other_senses_cnt = sum(synset_counter.values()) - max(synset_counter.values())
        if (
            is_majority_sense_more_than(
                synset_counter, cutoff=MAJORITY_SENSE_DESIRED_MAX_CUTOFF
            )
            and other_senses_cnt > 0
        ):
            # instances where the majority sense examples are more than MAJORITY_SENSE_DESIRED_MAX_CUTOFF
            # of all examples
            (
                senses,
                number_to_generate_for_each_sense,
            ) = get_non_majority_senses_for_which_to_generate_examples_and_count(
                synset_counter
            )
            lemma_pos__to__synset_count_to_generate[lemma_pos] = {
                sense: number_to_generate_for_each_sense for sense in senses
            }
        else:
            # all other cases assuming that any sense has less than 1/max_ratio examples
            max_ratio = 10

            senses_for_which_to_generate_and_how_many = [
                (sense, math.ceil((majority_sense_cnt - max_ratio * cnt) / max_ratio))
                for sense, cnt in synset_counter.items()
                if cnt > 0 and cnt * max_ratio < majority_sense_cnt
            ]
            if len(senses_for_which_to_generate_and_how_many) == 0:
                continue

            for sense, how_many in senses_for_which_to_generate_and_how_many:
                lemma_pos__to__synset_count_to_generate[lemma_pos] = {
                    sense: min(how_many, MAX_SENTENCES_TO_GENERATE)
                }
    return lemma_pos__to__synset_count_to_generate


def generate_input():
    (
        _,
        _,
        _,
        _,
        _,
        sent_id_to_sentence,
        lemma_pos__to__existing_synset_count,
        lemma_pos_synset__to__instance_ids,
    ) = get_dataset_mappings()
    lemma_pos__to__synset_count_to_generate = (
        get_lemma_pos__to__synset_count_to_generate(
            lemma_pos__to__existing_synset_count
        )
    )

    with open(OUTPUT_PATH, "w", newline="") as csvfile:
        fieldnames = [
            "index",
            "lemma",
            "human_readable_pos",
            "synset_key_name",
            "definition",
            "example",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        i = 0
        for (
            lemma,
            pos,
        ), synset_to_count in lemma_pos__to__synset_count_to_generate.items():
            for synset, how_many_to_generate in synset_to_count.items():
                definition = synset.definition()
                example = get_example(
                    lemma,
                    pos,
                    synset,
                    lemma_pos_synset__to__instance_ids,
                    sent_id_to_sentence,
                )
                for _ in range(how_many_to_generate):
                    writer.writerow(
                        {
                            "index": i,
                            "lemma": lemma,
                            "human_readable_pos": SEMCOR_POS__TO__HUMAN_READABLE_POS[
                                pos
                            ],
                            "synset_key_name": synset,
                            "definition": definition,
                            "example": example,
                        }
                    )
                    i += 1


if __name__ == "__main__":
    generate_input()
