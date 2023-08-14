from smart_word_hints_api.app.hints_providers import EnglishToEnglishHintsProvider, Hint


def test__smoke():
    # from https://en.wikipedia.org/wiki/Palace_of_Assembly
    text = """
    After the partition of Punjab in 1947 following the independence of India, 
    the divided Punjab required a new capital to replace Lahore, which was now in Pakistan. 
    Prime Minister Jawaharlal Nehru commissioned Le Corbusier to build a new city 
    for the capital of Punjab. This city would become Chandigarh. Nehru desired that the city's 
    design be "unfettered by the traditions of the past, a symbol of the nation's faith in the future". 
    Subsequently, Corbusier and his team designed not just a large assembly and high court building, 
    but all major buildings in the city, down to the door handles in public offices.[1] 
    Construction of the Palace of Assembly began in 1951 and ended 11 years later in 1962. 
    The building was inaugurated on 15 April 1964.[7]"""

    hints_provider = EnglishToEnglishHintsProvider()
    print(hints_provider.get_hints(text, avoid_repetitions=True))


