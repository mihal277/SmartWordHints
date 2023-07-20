from nltk.corpus.reader import ADJ, ADJ_SAT, ADV, NOUN, VERB

EN_FREQUENCY_RANKING_RELATIVE_PATH: str = "assets/ranking_common_en.txt"
EN_AMALGUM_FREQUENCY_RANKING_RELATIVE_PATH: str = "assets/amalgum_freq_list.csv"
EN_PHRASAL_VERBS_RELATIVE_PATH: str = "assets/english_phrasal_verbs.txt"
EN_SIMPLE_DEFINITIONS_RELATIVE_PATH: str = "assets/simplified_definitions.csv"
DISTILROBERTA_MODEL_RELATIVE_PATH: str = "assets/models/wsd_distilroberta.bin"
ROBERTA_BASE_MODEL_RELATIVE_PATH: str = "assets/models/wsd_roberta_base.bin"
ROBERTA_LARGE_MODEL_RELATIVE_PATH: str = "assets/models/wsd_roberta_large.bin"

MAX_FREQUENCY_RANKING_SCORE_TO_CONSIDER_AS_EASY = 2000

CONFIG_FILENAME = "config.ini"
DEBUG_MODE_ENV_VAR = "API_DEBUG_MODE"
CONFIG_PROD_SECTION = "prod"
CONFIG_DEBUG_SECTION = "debug"
CONFIG_KEY_LAMBDAWARMER_SEND_METRIC = "lambdawarmer_send_metric"
CONFIG_KEY_MODEL_NAME = "model_name"

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

# from
# https://github.com/nusnlp/esr/blob/274353adb90d588889a6ccf46873666f3943d57e/code/esr/dataset/dataset_semcor_wngc.py#L18C7-L18C7
TAG__TO__WSD_XML_EXPECTED_POS = {
    "CC": "CONJ",
    "CD": "NUM",
    "DT": "DET",
    "EX": "DET",
    "FW": "X",
    "IN": "ADP",
    "JJ": "ADJ",
    "JJR": "ADJ",
    "JJS": "ADJ",
    "LS": "NUM",
    "MD": "VERB",
    "NN": "NOUN",
    "NNS": "NOUN",
    "NNP": "NOUN",
    "NNPS": "NOUN",
    "PDT": "DET",
    "POS": "PRT",
    "PRP": "PRON",
    "PRP$": "PRON",
    "RB": "ADV",
    "RBR": "ADV",
    "RBS": "ADV",
    "RP": "PRT",
    "SYM": ".",
    "TO": "PRT",
    "UH": "X",
    "VB": "VERB",
    "VBD": "VERB",
    "VBG": "VERB",
    "VBN": "VERB",
    "VBP": "VERB",
    "VBZ": "VERB",
    "WDT": "DET",
    "WP": "PRON",
    "WP$": "PRON",
    "WRB": "ADV",
    "$": ".",
    "#": ".",
    "``": ".",
    "''": ".",
    "(": ".",
    ")": ".",
    ",": ".",
    ".": ".",
    ":": ".",
    "-RRB-": ".",
    "-LRB-": ".",
}
DEFAULT_WSD_XML_EXPECTED_POS = ""

TRANSLATABLE_EN_POS = LEMMATIZABLE_EN_POS_TO_POS_SIMPLE.keys()

UNIVERSAL_POS_VERB = "VERB"
