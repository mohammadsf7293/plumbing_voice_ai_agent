# Testing

## Offline checks — no subscriptions or API keys

```bash
make setup-dev
make demo
make test
make test-coverage
```

Setup downloads the locked Python packages. The tests themselves require no network or model assets. Each offline test uses dummy credentials and blocks Python socket connections, including localhost; these placeholders cannot authenticate with providers.

The suite checks actual application logic:

- Booking format validation, deterministic future slots, retry behavior, reservation conflicts, cancellation, and session isolation.
- LiveKit tool adapters, including validation failures exposed as `ToolError`.
- Agent handoff state and the instructions passed to the receiving agent’s greeting.
- Streaming text cleanup across chunk boundaries, including the real SDK default TTS node with a fake transport returning an audio frame.
- The real worker entrypoint with provider/model constructors replaced by mocks.
- Real `AgentSession` event dispatch for structured metrics, tool outcomes, and errors.

Tests do not establish speech recognition accuracy, model reasoning quality, pronunciation, acoustic quality, provider reliability, or deployed connectivity. A fake audio frame proves pipeline wiring, not synthesized speech quality.

## Provider evaluations — explicit opt-in

The existing conversation tests are marked `provider`. They are collected but skipped unless enabled:

```bash
make env-setup
# Configure actual provider credentials in .env.local.
make test-provider
# Or select one evaluation:
uv run --locked --extra dev pytest --run-provider -m provider tests/test_final.py -k greeting
```

These evaluations can call paid services. They remain a legacy, unverified suite: offline success does not imply these tests pass. Their fixtures and model judgments may require further work when a live environment is available. Do not use their skipped count as evidence of tested conversation behavior.

`python run_tests.py` forwards arguments to pytest and uses the same offline default. `make test-behavior` is an alias for the explicit provider run.

## Container check

```bash
docker build -t plumbing-voice-agent .
docker run --rm plumbing-voice-agent python -m plumbing.demo
```

The build resolves dependencies from `uv.lock` and downloads public model files as the non-root runtime user. Running the scripted demo inside the image verifies Linux imports and the business workflow without credentials; it does not verify LiveKit Cloud deployment.
