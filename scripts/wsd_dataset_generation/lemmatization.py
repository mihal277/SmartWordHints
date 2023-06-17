import spacy

nlp_en = spacy.load("en_core_web_trf")

LemmatizedSentence = list[tuple[str, str, str]]


def lemmatize_sentence(sentence: str) -> LemmatizedSentence:
    nlp_en(sentence)
    return [(token.text, token.lemma_, token.pos_) for token in nlp_en(sentence)]
