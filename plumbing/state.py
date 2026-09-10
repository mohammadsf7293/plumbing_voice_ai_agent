from dataclasses import dataclass, field
from uuid import uuid4
from livekit.agents import Agent
from .business import DemoStore


@dataclass
class UserData:
    prev_agent: Agent | None = None
    agents: dict[str, Agent] = field(default_factory=dict)
    problem_description: str | None = None
    store: DemoStore = field(default_factory=DemoStore)
    session_id: str = field(default_factory=lambda: uuid4().hex)
