from smart_word_hints_api.app.hints_providers import EnglishToEnglishHintsProvider


def test_personal_pronouns_dont_raise_exceptions__smoke_test():
    hints_provider = EnglishToEnglishHintsProvider()
    hints_provider.get_hints("You are very nice", 0)
