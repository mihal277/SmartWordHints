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

### Verifying the correctness of the generated sentences
```commandline
OPENAI_API_KEY=<OPENAI_API_KEY> python verify_examples.py
```