# Assets

## [ranking_common_en.txt](ranking_common_en.txt)

(legacy) English words sorted from more to less common.

## amalgum_*.csv

Word frequency lists obtained by running the state-of-the-art 
WSD system ConSeC (<https://github.com/SapienzaNLP/consec>) on a 4 million tokens 
English corpus AMALGUM (<https://github.com/gucorpling/amalgum>), including data from Reddit.

This allows to show hints only for senses that are less common.
For example, a hint for `bank` might be shown in the sentence 
`By the time we reached the opposite bank, the boat was sinking fast.`, 
as the lemma bank in this context is not so frequent , but not in the sentence 
`I went to the bank to deposit some money`.

### [amalgum_freq_list.csv](amalgum_freq_list.csv)

A |-delimited CSV file that lists the (lemma,sense,pos) tuples from more to less common.

### [amalgum_freq_list__lemma_pos.csv](amalgum_freq_list__lemma_pos.csv)

A |-delimited CSV file that lists the (lemma,pos) tuples from more to less common.


### [amalgum_freq_list__lemma.csv](amalgum_freq_list__lemma.csv)

A |-delimited CSV file that lists the lemmas from more to less common.

## [english_phrasal_verbs.txt](english_phrasal_verbs.txt)

List of English phrasal verbs scraped from `wiktionary.org`.

Scraped using `scripts/scrapers/scrape_wiktionary_phrasal_verbs_list.py`.
Then the phrasal verbs that were have no WordNet translations
were filtered out using `scripts/assets_postprocessing/clean_phrasal_verbs_list.py`.

## [simplified_definitions.csv](simplified_definitions.csv)

Simplified WordNet definitions from `amalgum_freq_list.csv` using GPT3 (see `scripts/simple_definitions`).