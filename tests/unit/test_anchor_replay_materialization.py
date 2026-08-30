"""End-to-end proof that an injected anchor keeps a replayable request body.

The production failure this covers: a continuation carried only
``previous_response_id`` plus a small suffix.  When upstream rejected that
anchor (stale, or owned by an account that had just been drained), the bridge
had no complete body to send to a replacement account and terminated the
client stream instead.  These tests exercise the real projector chain rather
than a mock, so they fail if the rebuilt request stops being something the
Responses endpoint would accept on a different account.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from app.modules.proxy._service.support import materialize_anchor_replay_text
from app.modules.proxy.replay_safety import responses_payload_is_account_neutral_fresh_replay


def _sse(payload: dict[str, Any]) -> str:
    return f"event: {payload['type']}\ndata: {json.dumps(payload)}\n\n"


def _turn(*, request_text: str, output: list[dict[str, Any]]) -> SimpleNamespace:
    """One durable turn: the request body plus its terminal event spool."""

    return SimpleNamespace(
        operation=SimpleNamespace(request_text=request_text),
        events=[_sse({"type": "response.completed", "response": {"output": output}})],
    )


def _user(text: str) -> dict[str, Any]:
    return {"type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}


class _DurableBridge:
    def __init__(self, transcript: list[SimpleNamespace] | None) -> None:
        self._transcript = transcript
        self.requested_response_ids: list[str] = []

    async def get_replayable_transcript(self, *, response_id: str, **_kwargs: Any) -> Any:
        self.requested_response_ids.append(response_id)
        return self._transcript


@pytest.mark.asyncio
async def test_anchor_replay_rebuilds_full_transcript_with_tool_chain() -> None:
    # Turn 1: the user asks for something and the model answers with a tool call.
    # Turn 2: the client returns the tool output and the model replies.
    # The current turn then sends only a delta plus the anchor.
    transcript = [
        _turn(
            request_text=json.dumps({"model": "gpt-5.1", "input": [_user("list the files")]}),
            output=[
                {
                    "type": "function_call",
                    "id": "fc_owned_by_old_account",
                    "call_id": "call_1",
                    "name": "shell",
                    "arguments": '{"cmd":"ls"}',
                    "status": "completed",
                }
            ],
        ),
        _turn(
            request_text=json.dumps(
                {
                    "model": "gpt-5.1",
                    "input": [{"type": "function_call_output", "call_id": "call_1", "output": "a.txt"}],
                }
            ),
            output=[
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "There is one file."}],
                    "id": "msg_owned_by_old_account",
                    "status": "completed",
                }
            ],
        ),
    ]
    bridge = _DurableBridge(transcript)

    replay_text = await materialize_anchor_replay_text(
        bridge,
        anchor_response_id="resp_owned_by_old_account",
        current_request_text=json.dumps({"model": "gpt-5.1", "input": [_user("now delete it")]}),
    )

    assert replay_text is not None, "a complete durable chain must rebuild a replayable body"
    payload = json.loads(replay_text)
    assert payload["type"] == "response.create"
    body = {key: value for key, value in payload.items() if key != "type"}

    # The anchor is gone: that is the whole point, the body must not depend on
    # state owned by the drained account.
    assert "previous_response_id" not in body or body["previous_response_id"] in (None, "")

    # Every turn survived, in order, and the current suffix is last.
    texts = [
        content["text"]
        for item in body["input"]
        if isinstance(item, dict)
        for content in (item.get("content") or [])
        if isinstance(content, dict) and "text" in content
    ]
    assert texts == ["list the files", "There is one file.", "now delete it"]

    # The tool call and its output are both present and still paired.
    call_ids = [item.get("call_id") for item in body["input"] if isinstance(item, dict) and item.get("call_id")]
    assert call_ids == ["call_1", "call_1"]
    types = [item.get("type") for item in body["input"] if isinstance(item, dict)]
    assert types.index("function_call") < types.index("function_call_output")

    # Response-owned item ids must not travel to another account.
    assert all(item.get("id") in (None, "") for item in body["input"] if isinstance(item, dict))

    # And the result is genuinely portable by the shared contract check.
    assert responses_payload_is_account_neutral_fresh_replay(body, allow_file_references=True)
    assert bridge.requested_response_ids == ["resp_owned_by_old_account"]


@pytest.mark.asyncio
async def test_anchor_replay_fails_closed_when_transcript_incomplete() -> None:
    # An incomplete spool must never be papered over: replaying a partial
    # conversation silently loses context, which is worse than reporting the
    # failure. ``get_replayable_transcript`` returns None for that case.
    assert (
        await materialize_anchor_replay_text(
            _DurableBridge(None),
            anchor_response_id="resp_missing",
            current_request_text=json.dumps({"model": "gpt-5.1", "input": [_user("hi")]}),
        )
        is None
    )


@pytest.mark.asyncio
async def test_anchor_replay_fails_closed_on_unsettled_tool_call() -> None:
    # The last turn left a tool call the client never answered.  Rebuilding a
    # body with a dangling call would be rejected upstream, so the projector
    # must refuse rather than hand back an invalid request.
    transcript = [
        _turn(
            request_text=json.dumps({"model": "gpt-5.1", "input": [_user("run it")]}),
            output=[
                {
                    "type": "function_call",
                    "call_id": "call_never_answered",
                    "name": "shell",
                    "arguments": "{}",
                    "status": "completed",
                }
            ],
        )
    ]

    replay_text = await materialize_anchor_replay_text(
        _DurableBridge(transcript),
        anchor_response_id="resp_dangling",
        current_request_text=json.dumps({"model": "gpt-5.1", "input": [_user("never mind")]}),
    )

    assert replay_text is None


@pytest.mark.asyncio
async def test_anchor_replay_does_not_duplicate_a_client_full_resend() -> None:
    # Codex may reconnect and resend its whole local transcript while the
    # proxy also holds it durably.  Appending both would double every turn.
    transcript = [
        _turn(
            request_text=json.dumps({"model": "gpt-5.1", "input": [_user("first")]}),
            output=[
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "ok"}],
                    "status": "completed",
                }
            ],
        )
    ]
    full_resend = {
        "model": "gpt-5.1",
        "input": [
            _user("first"),
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "ok"}],
                "status": "completed",
            },
            _user("second"),
        ],
    }

    replay_text = await materialize_anchor_replay_text(
        _DurableBridge(transcript),
        anchor_response_id="resp_full_resend",
        current_request_text=json.dumps(full_resend),
    )

    assert replay_text is not None
    body = json.loads(replay_text)
    texts = [
        content["text"]
        for item in body["input"]
        if isinstance(item, dict)
        for content in (item.get("content") or [])
        if isinstance(content, dict) and "text" in content
    ]
    assert texts == ["first", "ok", "second"]
