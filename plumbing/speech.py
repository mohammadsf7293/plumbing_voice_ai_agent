"""Text cleanup at LiveKit's streaming TTS node, shared by every agent."""
from collections.abc import AsyncIterable
import re
from livekit import rtc
from livekit.agents import Agent, ModelSettings


def clean_text(text: str) -> str:
    text = re.sub(r"(?m)^(\s*)[-#>]+(?=\s)", r"\1", text)
    return re.sub(r"[*_`~]", "", text)


async def clean_stream(text: AsyncIterable[str]) -> AsyncIterable[str]:
    # Hold only a possible line prefix. Do not buffer a whole response or line.
    prefix = ""
    at_start = True
    async for chunk in text:
        output = []
        for char in re.sub(r"[*_`~]", "", chunk):
            if at_start and char in "-#>":
                prefix += char
                continue
            if at_start:
                if not char.isspace():
                    output.append(prefix)
                prefix = ""
                at_start = char.isspace()
            output.append(char)
            if char == "\n":
                at_start = True
        if output:
            yield "".join(output)
    if prefix:
        yield prefix


class VoiceAgent(Agent):
    async def tts_node(self, text: AsyncIterable[str], model_settings: ModelSettings) -> AsyncIterable[rtc.AudioFrame]:
        async for frame in Agent.default.tts_node(self, clean_stream(text), model_settings):
            yield frame
