EN_FREQUENCY_RANKING_PATH = "ranking_common_en.txt"

EN = "english"
PL = "polish"


LEMMATIZABLE_POS_TO_POS_SIMPLE = {
    "JJ": "a",  # adjective or numeral, ordinal
    "JJR": "a",  # adjective, comparative
    "JJS": "a",  # adjective, superlative
    "RB": "r",  # adverb
    "RBR": "r",  # adverb, comparative
    "RBS": "r",  # adverb, superlative
    "NN": "n",  # noun, common, singular or mass
    "NNP": "n",  # noun, proper, singular
    "NNS": "n",  # noun, common, plural
    "VB": "v",  # verb, base form
    "VBD": "v",  # verb, past tense
    "VBG": "v",  # verb, present participle or gerund
    "VBN": "v",  # verb, past participle
    "VBP": "v",  # verb, present tense, not 3rd person singular
    "VBZ": "v",  # verb, present tense, 3rd person singular
}
