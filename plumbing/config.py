"""Check runtime configuration without exposing secret values."""
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

REQUIRED_KEYS = ("LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "OPENAI_API_KEY", "CARTESIA_API_KEY", "DEEPGRAM_API_KEY")


def validate_environment() -> None:
    missing = [name for name in (*REQUIRED_KEYS, "LIVEKIT_URL")
               if not os.environ.get(name, "").strip() or os.environ[name].startswith("<")]
    if missing:
        raise ValueError("Missing configuration: " + ", ".join(missing))
    url = urlparse(os.environ["LIVEKIT_URL"])
    if url.scheme not in ("ws", "wss") or not url.hostname:
        raise ValueError("LIVEKIT_URL must be a ws:// or wss:// URL.")


def load_environment() -> None:
    load_dotenv(".env.local")
