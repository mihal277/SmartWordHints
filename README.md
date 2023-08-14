# SmartWordHints

[![Tests](https://github.com/mihal277/SmartWordHints/actions/workflows/run-tests.yml/badge.svg)](https://github.com/mihal277/SmartWordHints/actions/workflows/run-tests.yml)

## API

### (Required) Downloading the model for word sense disambiguation

There are three options: 

`distilroberta` - fastest but least efficient: 

Download the model from <https://drive.google.com/file/d/1mdDdvwat3M6OIbSCmKnBOqNFF2iz3vdp/view?usp=sharing>
and put it as `smart_word_hints_api/app/assets/models/wsd_distilroberta.bin`

The other models have to be downloaded from the repository of the authors of ESR: <https://github.com/nusnlp/esr#using-trained-models>.

`roberta-base` - slower but better:

Copy `experiment/esr/roberta-base/dataset_semcor_wngc/sd_42/rtx3090_b32_b32_lr8.5e-6/model/pytorch_model.bin` to 
`smart_word_hints_api/app/assets/models` as `wsd_roberta_base.bin`.

Then, change `model_name` in `config.ini` to `roberta-base`.

`roberta-large` - slowest but best:

Copy `experiment/esr/roberta-large/dataset_semcor_wngc/sd_42/a100_b16_b16_lr8.5e-6_lim348/model/pytorch_model.bin` to 
`smart_word_hints_api/app/assets/models` as `wsd_roberta_large.bin`.

Then, change `model_name` in `config.ini` to `roberta-large`.

### Running the API locally inside Docker
```
./scripts/run_local_docker.sh 8081
```

### Running the API locally without Docker

#### Virtualenv
```
virtualenv -p python3.9 venv
source venv/bin/activate
```

#### Installing the requirements
```
pip install -r smart_word_hints_api/requirements/requirements.txt
python -m spacy download $(cat smart_word_hints_api/requirements/spacy_modules.txt)
python -m nltk.downloader $(cat smart_word_hints_api/requirements/nltk_modules.txt)
git clone https://github.com/mihal277/esr.git -b replace-getchildren smart_word_hints_api/app
```

#### Running the API:
```
./scripts/run_local.sh
```

### Urls

After running the above commands:
* the main API endpoint is available at `localhost:8081/api/get_hints`
* the API docs are available at `localhost:8081/docs`

## Testing

To run tests without Docker:
```
./scripts/run_api_tests.sh
```

To run tests in Docker:
```
./scripts/run_api_tests_docker.sh
```