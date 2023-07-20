from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import Literal
from xml.etree import ElementTree as ET

import torch
import transformers
from nltk.corpus import wordnet as wn

from smart_word_hints_api.app.constants import (
    DEFAULT_WSD_XML_EXPECTED_POS,
    DISTILROBERTA_MODEL_RELATIVE_PATH,
    ROBERTA_BASE_MODEL_RELATIVE_PATH,
    ROBERTA_LARGE_MODEL_RELATIVE_PATH,
    TAG__TO__WSD_XML_EXPECTED_POS,
)
from smart_word_hints_api.app.distilroberta_for_wsd import DistilRobertaForWsd
from smart_word_hints_api.app.esr.code.esr.dataset.dataset_semcor_wngc import (
    DataCollatorForWsd,
    WsdDataset,
)
from smart_word_hints_api.app.esr.code.esr.model import RobertaForWsd
from smart_word_hints_api.app.text_holder import TextHolderEN
from smart_word_hints_api.app.token_wrappers import TokenEN

ESRModels = Literal["distilroberta-base", "roberta-base", "roberta-large"]


class ESRSenseProvider:
    def __init__(self, model_name: ESRModels) -> None:
        self.model_name = model_name
        self.config = transformers.AutoConfig.from_pretrained(self.model_name)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.model_name)
        self.model = self._get_model()

    def _get_model(self) -> RobertaForWsd | DistilRobertaForWsd:
        if self.model_name == "distilroberta-base":
            return DistilRobertaForWsd.from_pretrained(
                Path(__file__).parent / DISTILROBERTA_MODEL_RELATIVE_PATH,
                config=self.config,
            )
        if self.model_name == "roberta-base":
            return DistilRobertaForWsd.from_pretrained(
                Path(__file__).parent / ROBERTA_BASE_MODEL_RELATIVE_PATH,
                config=self.config,
            )
        if self.model_name == "roberta-large":
            return DistilRobertaForWsd.from_pretrained(
                Path(__file__).parent / ROBERTA_LARGE_MODEL_RELATIVE_PATH,
                config=self.config,
            )
        raise ValueError(f"Unknown model name {self.model_name}")

    def get_sense_keys(
        self, text_holder: TextHolderEN, token_indexes_to_disambiguate: list[int]
    ) -> dict[int, str]:
        with tempfile.NamedTemporaryFile(
            prefix=f"prefix_{uuid.uuid4()}_", mode="w+t"
        ) as f:
            dataset_element_id__to__token_id = save_input_as_xml(
                text_holder.tokens,
                token_indexes_to_disambiguate,
                f.name,
            )

            temporary_dataset = WsdDataset(
                self.tokenizer,
                limit=432,
                wsd_xml=f.name,
                wsd_label=None,
                annotators=None,
                is_dev=False,
                is_main_process=False,
                extra_xml=None,
            )

            dataset_element_id__to__sense = self._get_sense_keys(temporary_dataset)
            return {
                dataset_element_id__to__token_id[dataset_element_id]: sense
                for dataset_element_id, sense in dataset_element_id__to__sense.items()
            }

    def _get_sense_keys(self, temporary_dataset: WsdDataset) -> dict[str, str]:
        batch = DataCollatorForWsd()(temporary_dataset)
        with torch.no_grad():
            preds = self.model(**batch)[0]

        examples = temporary_dataset.get_example_list()

        assert len(preds) == len(examples)
        result_softmax = {}
        for (instance_id, sense_key, *_), pred in zip(examples, preds):
            result_softmax.setdefault(instance_id, {})
            result_softmax[instance_id][sense_key] = pred

        return {key: max(value, key=value.get) for key, value in result_softmax.items()}


def save_input_as_xml(
    input_tokens: list[TokenEN],
    token_indexes_to_disambiguate: list[int],
    temporary_xml_file_name: str,
) -> dict[str, int]:
    """
    To use esr with minimal modification, fake xml "dataset" is created, resembling
    the SemCor dataset.

    Returns the mapping from dataset id to token index, for example:
    d000.s000.t003 -> 1, d000.s000.t004 -> 2 etc.
    """

    dataset_id__to__token_id: dict[str, int] = {}

    token_indexes_to_disambiguate = set(token_indexes_to_disambiguate)

    corpus_element = ET.Element("corpus")
    text_element = ET.SubElement(corpus_element, "text", id="d000")

    sentence_element = ET.SubElement(text_element, "sentence", id="d000.s000")
    sentence_i = 0
    token_within_sentence_i = 0

    for token_i, token in enumerate(input_tokens):
        if token_i > 0 and token.is_sent_start():
            sentence_i += 1
            token_within_sentence_i = 0
            sentence_element = ET.SubElement(
                text_element, "sentence", id=f"d000.s{str(sentence_i).zfill(3)}"
            )

        if token_i in token_indexes_to_disambiguate:
            element_name = "instance"
        else:
            element_name = "wf"

        sub_element_id = (
            f"d000.s{str(sentence_i).zfill(3)}.t{str(token_within_sentence_i).zfill(3)}"
        )
        ET.SubElement(
            sentence_element,
            element_name,
            lemma=lemma_extended_if_is_in_wordnet_else_lemma(token),
            pos=TAG__TO__WSD_XML_EXPECTED_POS.get(
                token.tag, DEFAULT_WSD_XML_EXPECTED_POS
            ),
            id=sub_element_id,
        ).text = token.text

        dataset_id__to__token_id[sub_element_id] = token_i

        token_within_sentence_i += 1

    tree = ET.ElementTree(corpus_element)
    tree.write(temporary_xml_file_name)

    return dataset_id__to__token_id


def lemma_extended_if_is_in_wordnet_else_lemma(token: TokenEN) -> str:
    lemma_extended = "_".join(token.lemma_extended.split())
    if len(wn.synsets(lemma_extended)) > 0:
        return lemma_extended
    return token.lemma
