This requires a previously setup ollama docker container running on a network called 'ollama'.
The network can be called something else, but the `--network ollama` name below will have to be
changed.

Only ever needs to be run once:
```
docker network create ollama
```

```
docker build -t ollama-tools:0.0.1 .
```

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
