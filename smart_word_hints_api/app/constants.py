from nltk.corpus.reader import ADJ, ADJ_SAT, ADV, NOUN, VERB

EN_FREQUENCY_RANKING_PATH = "smart_word_hints_api/app/ranking_common_en.txt"

EN = "english"
PL = "polish"

ADJECTIVES = {ADJ, ADJ_SAT}

LEMMATIZABLE_POS_TO_POS_SIMPLE = {
    "JJ": ADJ,  # adjective or numeral, ordinal
    "JJR": ADJ,  # adjective, comparative
    "JJS": ADJ,  # adjective, superlative
    "RB": ADV,  # adverb
    "RBR": ADV,  # adverb, comparative
    "RBS": ADV,  # adverb, superlative
    "NN": NOUN,  # noun, common, singular or mass
    "NNP": NOUN,  # noun, proper, singular
    "NNS": NOUN,  # noun, common, plural
    "VB": VERB,  # verb, base form
    "VBD": VERB,  # verb, past tense
    "VBG": VERB,  # verb, present participle or gerund
    "VBN": VERB,  # verb, past participle
    "VBP": VERB,  # verb, present tense, not 3rd person singular
    "VBZ": VERB,  # verb, present tense, 3rd person singular
}
