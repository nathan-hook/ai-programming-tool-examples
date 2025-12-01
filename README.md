docker build -t ollama-tools:0.0.1 .

docker run --name python-agents --network ollama -it --rm -v ./code:/opt/code ollama-tools:0.0.1 /bin/bash

cd opt/code/

python3 ollama_what_tempature.py

python3 ollama_what_time_is_it.py