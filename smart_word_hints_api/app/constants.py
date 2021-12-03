from nltk.corpus.reader import ADJ, ADJ_SAT, ADV, NOUN, VERB

ASSETS_PATH: str = "smart_word_hints_api/app/assets"
EN_FREQUENCY_RANKING_PATH: str = ASSETS_PATH + "/ranking_common_en.txt"
EN_PHRASAL_VERBS_PATH: str = ASSETS_PATH + "/english_phrasal_verbs.txt"

EN: str = "english"
PL: str = "polish"

ADJECTIVES: set[str] = {ADJ, ADJ_SAT}

JJ = "JJ"
JJR = "JJR"
JJS = "JJS"
RB = "RB"
RBR = "RBR"
RBS = "RBS"
NN = "NN"
NNP = "NNP"
NNS = "NNS"
VB = "VB"
VBD = "VBD"
VBG = "VBG"
VBN = "VBN"
VBP = "VBP"
VBZ = "VBZ"

LEMMATIZABLE_EN_POS_TO_POS_SIMPLE: dict[str, str] = {
    JJ: ADJ,  # adjective or numeral, ordinal
    JJR: ADJ,  # adjective, comparative
    JJS: ADJ,  # adjective, superlative
    RB: ADV,  # adverb
    RBR: ADV,  # adverb, comparative
    RBS: ADV,  # adverb, superlative
    NN: NOUN,  # noun, common, singular or mass
    NNP: NOUN,  # noun, proper, singular
    NNS: NOUN,  # noun, common, plural
    VB: VERB,  # verb, base form
    VBD: VERB,  # verb, past tense
    VBG: VERB,  # verb, present participle or gerund
    VBN: VERB,  # verb, past participle
    VBP: VERB,  # verb, present tense, not 3rd person singular
    VBZ: VERB,  # verb, present tense, 3rd person singular
}

TRANSLATABLE_EN_POS = LEMMATIZABLE_EN_POS_TO_POS_SIMPLE.keys()

UNIVERSAL_POS_VERB = "VERB"
