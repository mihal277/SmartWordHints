## Setup

Create virtualenv with python3.10. Then:

```commandline
git clone https://github.com/mihal277/esr.git -b replace-getchildren
pip install -r requirements.txt
python -m nltk.downloader $(cat nltk_modules.txt)
python -m spacy download $(cat spacy_modules.txt)
```

Finally, download the trained ESR models 
([README.md](esr%2FREADME.md) -> section `Using trained models`)

## Running

### Generate new sentences

```commandline
OPENAI_API_KEY=<OPENAI_API_KEY> python get_new_sentences_with_chat_gpt.py
```