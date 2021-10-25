# SmartWordHints

## API

### Running the API locally inside Docker
```
sudo ./scripts/run_local_docker.sh 8081
```

### Running the API locally without Docker
First, create a virtualenv and activate it:
```
virtualenv -p python3.9 venv
source venv/bin/activate
```

Install the requirements:
```
pip install -r smart_word_hints_api/requirements/requirements.txt
python -m nltk.downloader $(cat smart_word_hints_api/requirements/nltk_modules.txt)
```

Finally, run the API:
```
./scripts/run_local.sh
```

### Urls

After running the above commands:
* the main API endpoint is available at `localhost:8081/api/get_hints`
* the API docs are available at `localhost:8081/docs`

## Testing

To run tests outside:
```
./run_tests.sh
```

To make sure tests are automatically run before push:
```
git config core.hooksPath hooks/
```