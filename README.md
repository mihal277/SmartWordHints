# SmartWordHints

## Running the api locally using Docker

First, build the API image:
```
sudo docker build -t smart-word-hints smart-word-hints-api/
```

Then, run the image:
```
sudo docker run --name smart-word-hints -p 8081:8081 --rm -d smart-word-hints
```

The API is available at `localhost:8081`