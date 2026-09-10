"""Structured operational events; customer text and tool arguments are omitted."""
import json
import logging
from time import time

logger = logging.getLogger("plumbing.events")


def emit(session_id: str, event: str, **fields) -> None:
    logger.info(json.dumps({"timestamp": time(), "session_id": session_id, "event": event, **fields}))


def attach_session_events(session, session_id: str) -> None:
    @session.on("metrics_collected")
    def metrics(event):
        # Only numeric timing and usage fields, not arbitrary provider metadata.
        values = {key: value for key, value in event.metrics.model_dump().items()
                  if isinstance(value, (int, float)) and not isinstance(value, bool)}
        emit(session_id, "metrics", provider_stage=event.metrics.type, **values)

    @session.on("function_tools_executed")
    def tools(event):
        for call, output in event.zipped():
            emit(session_id, "tool_result", tool=call.name, call_id=call.call_id,
                 status="missing" if output is None else "error" if output.is_error else "ok")

    @session.on("agent_state_changed")
    def state(event):
        emit(session_id, "agent_state", previous=event.old_state, current=event.new_state)

    @session.on("error")
    def error(event):
        emit(session_id, "provider_error", source=type(event.source).__name__,
             error_type=type(event.error).__name__)
