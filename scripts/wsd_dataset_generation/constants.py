from nltk.corpus import wordnet as wn

VERIFICATION_KEYS = [
    "v__contains_lemma",  # whether the lemma with correct pos is even in the sentence
    "v__esr_base",  # bool: Correct or Incorrect
    "v__esr_base_score",  # score of the expected synset
    "v__esr_base_highest_score",  # score of the highest-scored synset
    "v__esr_large",  # bool: Correct or Incorrect
    "v__esr_large_score",  # score of the expected synset
    "v__esr_large_highest_score",  # score of the highest-scored synset
    "v__gpt35__disambiguate",  # bool: Correct or Incorrect
    "v__gpt35__verify",  # bool: Correct or Incorrect
    "v__number_of_successes",  # number of successes for gpt and esr
    "v__number_of_possible_synsets",  # how many senses a given word with given pos has
]

WORDNET_POS__TO__HUMAN_READABLE_POS = {
    wn.ADJ: "adjective",
    wn.ADJ_SAT: "adjective",
    wn.ADV: "adverb",
    wn.NOUN: "noun",
    wn.VERB: "verb",
}

WORDNET_POS__TO__LEMMATIZATION_POS = {
    wn.ADJ: "ADJ",
    wn.ADJ_SAT: "ADJ",
    wn.ADV: "ADV",
    wn.NOUN: "NOUN",
    wn.VERB: "VERB",
}
