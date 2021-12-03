# Assets

## ranking_common_en.txt

English words sorted from more to less common.

## english_phrasal_verbs.txt

List of English phrasal verbs scraped from `wiktionary.org`.

Scraped using `scripts/scrapers/scrape_wiktionary_phrasal_verbs_list.py`.
Then the phrasal verbs that were have no WordNet translations
were filtered out using `scripts/assets_postprocessing/clean_phrasal_verbs_list.py`.