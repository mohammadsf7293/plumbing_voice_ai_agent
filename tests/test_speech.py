from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from livekit import rtc
from livekit.agents import Agent
from plumbing.speech import clean_stream, clean_text, VoiceAgent


async def chunks(values):
    for value in values:
        yield value


@pytest.mark.parametrize('text,expected', [
    ('**Leaky** kitchen-sink: 512-555-0123', 'Leaky kitchen-sink: 512-555-0123'),
    ('# Heading\n- **Call** us\n> Thanks', ' Heading\n Call us\n Thanks'),
    ('-5 degrees, A > B, ticket #123', '-5 degrees, A > B, ticket #123'),
    ('', ''), ('~Hello~', 'Hello'),
])
async def test_stream_cleanup_across_every_chunk_boundary(text, expected):
    assert clean_text(text) == expected
    for index in range(len(text) + 1):
        assert ''.join([v async for v in clean_stream(chunks([text[:index], text[index:]]))]) == expected
    assert ''.join([v async for v in clean_stream(chunks(list(text)))]) == expected


async def test_real_sdk_tts_node_receives_clean_stream(monkeypatch):
    # Exercise Agent.default.tts_node, replacing only the outbound TTS transport.
    frame = rtc.AudioFrame.create(sample_rate=24000, num_channels=1, samples_per_channel=240)

    class Transport:
        def __init__(self):
            import asyncio
            self.finished = asyncio.Event()
            self.input = []
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        def push_text(self, value):
            self.input.append(value)
        def end_input(self):
            self.finished.set()
        async def __aiter__(self):
            await self.finished.wait()
            yield SimpleNamespace(frame=frame)

    transport = Transport()
    tts = SimpleNamespace(capabilities=SimpleNamespace(streaming=True), stream=Mock(return_value=transport))
    activity = SimpleNamespace(tts=tts, session=SimpleNamespace(conn_options=SimpleNamespace(tts_conn_options=None)))
    monkeypatch.setattr(Agent, '_get_activity_or_raise', lambda self: activity)
    voice = VoiceAgent(instructions='Test')
    output = [v async for v in voice.tts_node(chunks(['**Hello', '** kitchen-', 'sink']), None)]
    assert output == [frame]
    assert ''.join(transport.input) == 'Hello kitchen-sink'
    tts.stream.assert_called_once_with(conn_options=None)


async def test_trailing_literal_prefix_is_preserved():
    assert ''.join([v async for v in clean_stream(chunks(['ticket ', '#']))]) == 'ticket #'
    assert ''.join([v async for v in clean_stream(chunks(['#']))]) == '#'
