from nltk import WordNetLemmatizer
from nltk import pos_tag, word_tokenize

lemmatizer = WordNetLemmatizer()
words = "President Joe Biden plans to announce new executive actions on guns on Thursday, a person familiar with the plans said, fulfilling a commitment he made in the aftermath of two deadly shootings last month."
words = pos_tag(word_tokenize(words))
for word, pos in words:
    print(pos)
    pos_simple = pos[0].lower()
    pos_simple = pos_simple if pos_simple in ['a', 'r', 'n', 'v'] else None
    print("pos_simple: ", pos_simple)
    if pos_simple is None:
        print(word)
    else:
        res = lemmatizer.lemmatize(word, pos_simple)
        print(res)
    print(); print()
