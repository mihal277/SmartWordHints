from typing import List, Tuple, Optional

from nltk import FreqDist, tokenize, pos_tag
from nltk.corpus import brown, wordnet, WordNetCorpusReader
from nltk.stem import WordNetLemmatizer



# TODO jak są parsowane rzeczowniki składające się z dwóch słów



def get_lemma(word, pos):
    lemmatizer = WordNetLemmatizer()
    pos_simple = pos[0].lower()
    pos_simple = pos_simple if pos_simple in ['a', 'r', 'n', 'v'] else None
    if pos_simple is None:
        return word
    return lemmatizer.lemmatize(word, pos_simple)


def get_lemmas(words, with_pos=False):
    words = [word.lower() if word != "I" else word for word in words]
    words = pos_tag(words)
    result = []
    for word, pos in words:
        if not with_pos:
            result.append(get_lemma(word, pos))
        else:
            result.append((get_lemma(word, pos), pos))
    return result


def get_tokens_with_spans(text: str) -> List[Tuple[int, int]]:
    tokens = tokenize.word_tokenize(text)
    offset = 0
    for token in tokens:
        offset = text.find(token, offset)
        yield token, offset, offset + len(token)
        offset += len(token)


def get_hint(word: str, start: int, end: int, pos=None) -> Optional[dict]:
    try:
        definition = wordnet.synsets(word)[0].definition()
    except IndexError:
        return None

    try:
        ranking = words_ranking.index(word)
    except ValueError:
        ranking = None

    return {
        "word": word,
        "start": start,
        "end": end,
        "ranking": ranking,
        "definition": definition,
    }


# words_lemmatized = get_lemmas(brown.words())
# words_freq_brown: FreqDist = FreqDist(words_lemmatized)
# words_ranking: List[str] = [
#     freq[0] for freq in words_freq_brown.most_common(len(words_freq_brown))
# ]
# with open("ranking_common_en.txt", "w") as f:
#     for word in words_ranking:
#         f.write(f"{word}\n")

with open("ranking_common_en.txt", "r") as f:
    words_ranking = f.read().splitlines()
# print(words_ranking)
#
# print(words_ranking[:1000])


def get_hints(article: str, difficulty: int):
    most_common = words_ranking[: difficulty]
    hints = []
    lemmas = get_lemmas(tokenize.word_tokenize(article), with_pos=True)
    tokens_with_spans = list(get_tokens_with_spans(article))
    for (word, start, end), (lemma, pos) in zip(tokens_with_spans, lemmas):
        if lemma not in most_common:
            hint = get_hint(lemma, start, end, pos)
            if hint is not None:
                hints.append(hint)
    return {"hints": hints}

# print(get_hints("Power is returning in the state and temperatures are set to rise but some 13 million people are still facing difficulties accessing clean water.", 2000))

# from nltk.corpus import wordnet as wn
# print(wn.langs())



words = ["access", "recommend", "engine", "injure"]

for word in words:
    synsets = wordnet.synsets(word)
    for synset in synsets:
        print("Synset: ", synset)
        print("Lemmas pol: ", synset.lemmas(lang="pol"))
        print("Lemmas en: ", synset.lemmas())
        print("Hypernyms: ", synset.hypernyms())
        print("Definition: ", synset.definition())
        print()
    print("\n\n\n")

