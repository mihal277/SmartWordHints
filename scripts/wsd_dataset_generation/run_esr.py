from typing import NamedTuple
from xml.etree import ElementTree as ET

import torch
import transformers
from esr.code.esr.dataset.dataset_semcor_wngc import DataCollatorForWsd, WsdDataset
from esr.code.esr.model import RobertaForWsd
from lemmatization import LemmatizedSentence, lemmatize_sentence
from nltk.corpus import wordnet as wn


class WSDResult(NamedTuple):
    top_synset: wn.synset
    synset__to__score: dict[wn.synset, float]


def get_config(model_name: str):
    return transformers.AutoConfig.from_pretrained(model_name)


def get_tokenizer(model_name: str):
    return transformers.AutoTokenizer.from_pretrained(model_name)


def get_pretrained_model(model, checkpoint_path: str, config):
    return model.from_pretrained(checkpoint_path, config=config)


CHECKPOINT_PATH_LARGE = (
    "esr/experiment/esr/roberta-large/"
    "dataset_semcor_wngc/sd_42/"
    "a100_b16_b16_lr8.5e-6_lim348/model/"
    "pytorch_model.bin"
)
MODEL_NAME_LARGE = "roberta-large"
config_large = get_config(MODEL_NAME_LARGE)
tokenizer_large = get_tokenizer(MODEL_NAME_LARGE)
pretrained_model_large = get_pretrained_model(
    RobertaForWsd, CHECKPOINT_PATH_LARGE, config_large
)


CHECKPOINT_PATH_BASE = (
    "esr/experiment/esr/roberta-base/"
    "dataset_semcor_wngc/sd_42/rtx3090_b32_b32_lr8.5e-6/"
    "model/pytorch_model.bin"
)
MODEL_NAME_BASE = "roberta-base"
config_base = get_config(MODEL_NAME_BASE)
tokenizer_base = get_tokenizer(MODEL_NAME_BASE)
pretrained_model_base = get_pretrained_model(
    RobertaForWsd, CHECKPOINT_PATH_BASE, config_base
)


def sentence_to_xml(
    lemmatized_sentence: LemmatizedSentence,
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
    for i, (word, lemma, pos) in enumerate(lemmatized_sentence):
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
            pos="VERB" if pos == "AUX" else pos,
            id=f"d000.s000.t{str(i).zfill(3)}",
        ).text = word

    if not at_least_one_instance_present:
        raise ValueError("no correct lemma_to_translate provided")

    tree = ET.ElementTree(corpus_element)
    tree.write(filename)


def disambiguate_sentence(
    lemmatized_sentence: LemmatizedSentence,
    lemma_to_disambiguate: str,
    lemma_to_disambiguate_i: int = 0,
    model_name: str = MODEL_NAME_LARGE,
) -> WSDResult:
    xml_path = "temp_xml.xml"
    sentence_to_xml(
        lemmatized_sentence, xml_path, lemma_to_disambiguate, lemma_to_disambiguate_i
    )

    if model_name == MODEL_NAME_LARGE:
        model = pretrained_model_large
        tokenizer = tokenizer_large
    elif model_name == MODEL_NAME_BASE:
        model = pretrained_model_base
        tokenizer = tokenizer_base
    else:
        raise ValueError(f"unknown model {model_name}")

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
        preds = model(**batch)[0]

    examples = dataset.get_example_list()

    assert len(preds) == len(examples)
    result_softmax = {}
    for (instance_id, sense_key, *_), pred in zip(examples, preds):
        result_softmax.setdefault(instance_id, {})
        result_softmax[instance_id][wn.synset_from_sense_key(sense_key)] = pred

    result = {}
    for instance_id, softmax_result in result_softmax.items():
        result.setdefault(instance_id)
        result[instance_id] = max(softmax_result, key=lambda x: softmax_result[x])

    assert len(result) == 1
    return WSDResult(
        top_synset=list(result.values())[0],
        synset__to__score={
            key: float(value) for key, value in list(result_softmax.values())[0].items()
        },
    )
