import argparse
import csv
import shutil
import xml.etree.ElementTree as ET

from constants import WORDNET_POS__TO__LEMMATIZATION_POS
from lemmatization import lemmatize_sentence
from nltk.corpus import wordnet as wn

FIRST_TEXT_ID = 352


def prettify_xml(input_path: str) -> None:
    with open(input_path, "r") as f:
        xml_str = f.read()
    xml_str = xml_str.replace("><", ">\n<")
    with open(input_path, "w") as f:
        f.write(xml_str)


def load_generated_sentences(
    input_generated_sentences: str, only_classified_as_correct: bool
) -> list[dict]:
    with open(input_generated_sentences, newline="", encoding="utf_8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="|")
        if not only_classified_as_correct:
            return list(reader)
        return [row for row in list(reader) if int(row["v__final_classification"]) == 1]


def sentence_to_xml_text_node(
    lemmatized_sentence: list[tuple],
    instance_lemma: str,
    instance_pos: str,
    text_node_id: int,
):
    text_node_id_str = "d" + str(text_node_id).zfill(3)
    text_element = ET.Element("text", id=text_node_id_str)
    sentence_element = ET.SubElement(
        text_element, "sentence", id=f"{text_node_id_str}.s000"
    )

    disambiguation_lemma_instance_id = None
    for i, (word, lemma, pos) in enumerate(lemmatized_sentence):
        element_name = "wf"
        instance_key = f"{text_node_id_str}.s000.t{str(i).zfill(3)}"
        if (
            lemma == instance_lemma
            and WORDNET_POS__TO__LEMMATIZATION_POS[instance_pos] == pos
        ):
            element_name = "instance"
            assert disambiguation_lemma_instance_id is None, "error: multiple instances"
            disambiguation_lemma_instance_id = instance_key

        ET.SubElement(
            sentence_element,
            element_name,
            lemma=lemma,
            pos="VERB" if pos == "AUX" else pos,
            id=instance_key,
        ).text = word

    return text_element, disambiguation_lemma_instance_id


def append_to_semcor(
    input_semcor_data: str,
    input_semcor_key: str,
    input_generated_sentences: str,
    output_extended_semcor_data: str,
    output_extended_semcor_key: str,
) -> None:
    generated_sentences_data = load_generated_sentences(
        input_generated_sentences, only_classified_as_correct=True
    )
    shutil.copyfile(input_semcor_key, output_extended_semcor_key)
    semcor_dataset_root = ET.parse(input_semcor_data).getroot()
    with open(output_extended_semcor_key, "a") as output_key_file:
        for i, generated_sentence_data in enumerate(
            generated_sentences_data, start=FIRST_TEXT_ID
        ):
            lemmatized_sentence = lemmatize_sentence(
                generated_sentence_data["new_sentence"]
            )

            synset = wn.synset(generated_sentence_data["synset_key_name"])
            text_element, instance_key = sentence_to_xml_text_node(
                lemmatized_sentence,
                instance_lemma=generated_sentence_data["lemma"],
                instance_pos=synset.pos(),
                text_node_id=i,
            )
            sense_keys = [
                lemma.key()
                for lemma in synset.lemmas()
                if lemma.name().lower() == generated_sentence_data["lemma"].lower()
            ]
            assert len(sense_keys) == 1, (
                sense_keys,
                generated_sentence_data["lemma"],
                synset,
            )
            output_line = f"{instance_key} {sense_keys[0]}\n"
            output_key_file.write(output_line)

            semcor_dataset_root.append(text_element)

    tree = ET.ElementTree(semcor_dataset_root)
    tree.write(output_extended_semcor_data)
    prettify_xml(output_extended_semcor_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_semcor_data", type=str, required=True)
    parser.add_argument("--input_semcor_key", type=str, required=True)
    parser.add_argument("--input_generated_sentences", type=str, required=True)
    parser.add_argument("--output_extended_semcor_data", type=str, required=True)
    parser.add_argument("--output_extended_semcor_key", type=str, required=True)
    args = parser.parse_args()
    append_to_semcor(
        args.input_semcor_data,
        args.input_semcor_key,
        args.input_generated_sentences,
        args.output_extended_semcor_data,
        args.output_extended_semcor_key,
    )
