# AI Programming Tool Examples

## Setup

Only ever needs to be run once:
```
docker network create ollama
```

Start Ollama and Open WebUI Containers
```
docker compose -f docker-compose-ollama.yml up
```

Add [qwen3:1.7b model](https://ollama.com/library/qwen3) via the Open WebUI interface:
http://localhost:3000

Create the python container that is used to run the example tool python scripts.
```
docker build -t ollama-tools:0.0.1 .
```

## Execution

The following command requires a previously setup ollama docker container running on a network called 'ollama'.
The network can be called something else, but the `--network ollama` name below will have to be
changed.

Run the python container.
```
docker run --name python-agents --network ollama -it --rm -v ./code:/opt/code ollama-tools:0.0.1 /bin/bash
```

```
cd opt/code/
```

```
python3 ollama_what_time_is_it.py
```

```
python3 ollama_what_time_is_it_inner_thoughts.py
```

```
python3 ollama_what_temperature.py
```

```
python3 ollama_what_temperature_inner_thoughts.py
```
