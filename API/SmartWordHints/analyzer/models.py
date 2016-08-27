from django.db import models

LANG_CHOICES = (
    ('en', 'English'),
    ('pl', 'Polish'),
)


class Word(models.Model):
    lang = models.CharField(max_length=2, choices=LANG_CHOICES)
    word = models.CharField(max_length=50)

    def __str__(self):
        return self.word


class Translation(models.Model):
    POS_CHOICES = (
        ('v', 'verb'),
        ('n', 'noun'),
        ('adv', 'adverb'),
        ('adj', 'adjective'),
        ('pron', 'pronoun'),
        ('prep', 'preposition'),
        ('conj', 'conjunction'),
        ('inter', 'interjection'),
    )
    part_of_speech = models.CharField(max_length=5, choices=POS_CHOICES)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    meaning = models.CharField(max_length=50)

    def __str__(self):
        return self.meaning
