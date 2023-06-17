import torch
from nltk.corpus import wordnet as wn
import transformers
import spacy
from xml.etree import ElementTree as ET

from esr.code.esr.model import RobertaForWsd
from esr.code.esr.dataset.dataset_semcor_wngc import WsdDataset, DataCollatorForWsd


def get_config(model_name: str):
    return transformers.AutoConfig.from_pretrained(model_name)


def get_tokenizer(model_name: str):
    return transformers.AutoTokenizer.from_pretrained(model_name)


def get_pretrained_model(model, checkpoint_path: str, config):
    return model.from_pretrained(checkpoint_path, config=config)


CHECKPOINT_PATH = (
    "esr/experiment/esr/roberta-large/"
    "dataset_semcor_wngc/sd_42/"
    "a100_b16_b16_lr8.5e-6_lim348/model/"
    "pytorch_model.bin"
)
MODEL_NAME = "roberta-large"

config = get_config(MODEL_NAME)
tokenizer = get_tokenizer(MODEL_NAME)
pretrained_model = get_pretrained_model(RobertaForWsd, CHECKPOINT_PATH, config)
nlp_en = spacy.load("en_core_web_trf")


def lemmatize_sentence(sentence: str) -> list[tuple[str, str, str]]:
    nlp_en(sentence)
    return [(token.text, token.lemma_, token.pos_) for token in nlp_en(sentence)]


def sentence_to_xml(
    sentence: str,
    filename: str,
    lemma_to_translate: str,
    inedex_of_lemma_to_translate: int,
) -> None:
    # we want to use esr without much modification, so we create a fake xml dataset
    # from the sentence

    corpus_element = ET.Element("corpus")
    text_element = ET.SubElement(corpus_element, "text", id="d000")
    sentence_element = ET.SubElement(text_element, "sentence", id="d000.s000")

    lemma_i = 0
    at_least_one_instance_present = False
    for i, (word, lemma, pos) in enumerate(lemmatize_sentence(sentence)):
        element_name = "wf"
        if lemma == lemma_to_translate:
            if lemma_i == inedex_of_lemma_to_translate:
                element_name = "instance"
                at_least_one_instance_present = True
            else:
                lemma_i += 1

        ET.SubElement(
            sentence_element,
            element_name,
            lemma=lemma,
            pos=pos,
            id=f"d000.s000.t{str(i).zfill(3)}",
        ).text = word

    if not at_least_one_instance_present:
        raise ValueError("no correct lemma_to_translate provided")

    tree = ET.ElementTree(corpus_element)
    tree.write(filename)



def disambiguate_sentence(
    sentence: str, lemma_to_disambiguate: str, lemma_to_disambiguate_i: int = 0
) -> wn.synset:
    xml_path = "temp_xml.xml"
    sentence_to_xml(sentence, xml_path, lemma_to_disambiguate, lemma_to_disambiguate_i)

    dataset = WsdDataset(
        tokenizer,
        limit=432,
        wsd_xml=xml_path,
        wsd_label=None,
        annotators=None,
        is_dev=False,
        is_main_process=True,
        extra_xml=None,
    )

    batch = DataCollatorForWsd()(dataset)
    with torch.no_grad():
        preds = pretrained_model(**batch)[0]

    examples = dataset.get_example_list()

    assert len(preds) == len(examples)
    result_softmax = {}
    for (instance_id, lemma_key, *_), pred in zip(examples, preds):
        result_softmax.setdefault(instance_id, {})
        result_softmax[instance_id][lemma_key] = pred

    result = {}
    for instance_id, softmax_result in result_softmax.items():
        result.setdefault(instance_id)
        result[instance_id] = max(softmax_result, key=lambda x: softmax_result[x])

    assert len(result) == 1
    return wn.synset_from_sense_key(list(result.values())[0])
