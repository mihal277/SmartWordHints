# SmartWordHints

## API

### Running the API locally using Docker

First, build the API image:
```
sudo docker build -t smart-word-hints smart-word-hints-api/
```

Then, run the image:
```
sudo docker run --name smart-word-hints -p 8081:8081 --rm -d smart-word-hints
```

Alternatively use:
```
sudo ./build_local.sh 8081
```

### Running the API locally without Docker

```
(cd smart-word-hints-api/app && uvicorn main:app --reload --port 8081)
```

### Urls

After running the above commands:
* the main API endpoint is available at `localhost:8081/api/get_hints`
* the API docs are available at `localhost:8081/docs`

## Testing

```
./run_tests.sh
```