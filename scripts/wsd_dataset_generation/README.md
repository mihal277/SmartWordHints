## Setup

Create virtualenv with python3.10. Then:

```commandline
git clone https://github.com/mihal277/esr.git -b replace-getchildren
pip install -r requirements.txt
python -m nltk.downloader $(cat nltk_modules.txt)
python -m spacy download $(cat spacy_modules.txt)
```

Finally, download the trained ESR models and datasets 
([README.md](esr%2FREADME.md) -> sections `Downloading Datasets` and `Using trained models`)

## Running

### Generate input data for generating new sentences

```commandline
python generate_input_for_dataset_creation.py
```

note: this was already done and the result is [input_data_sentences_to_generate.csv](input_data_sentences_to_generate.csv)

### Generate new sentences

```commandline
OPENAI_API_KEY=<OPENAI_API_KEY> python get_new_sentences_with_chat_gpt.py
```

note: this was already done and the result is [new_sentences.csv](new_sentences.csv)


### Verifying the correctness of the generated sentences (automatic)
```commandline
OPENAI_API_KEY=<OPENAI_API_KEY> python verify_examples.py --input new_sentences.csv --output new_sentences_verified.csv
```

### Verifying the correctness of the generated sentences (human)
```commandline
python human_verification.py --input new_sentences_verified.csv --output human_verification.csv --number_of_sentences 700
```

### Making a final classification of generated sentences
```commandline
python classify_verified_sentences.py --input_ai_verification new_sentences_verified.csv --input_human_verification human_verification.csv --no-use_normalizing --train_voting_model --metric_to_prioritize precision --secondary_metrics number_of_examples_used --min_score_for_secondary_metrics 0.6 --output_path classified__max_precision.csv
```
