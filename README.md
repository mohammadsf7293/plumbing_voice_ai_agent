# Simple voice agent serving calls of a fictitious piping company

## Project setup
- Sign up and register your API keys for for LiveKit, OpenAI, Cartesia, and DeepGram.
- Rename ".env.sample" to ".env.local" and fill API keys and other needed data.
- Download the project models via `uv run agent.py download-files`

## Running the project
You can either run the project using:
- `uv run agent.py console` to run the voice agent in the terminal
Or
- `uv run agent.py dev` and then running a web-frontend (or another client such as a mobile UI) to connect and talk to your agent
Note that for production environments, you should use `uv run agent.py start` instead.

