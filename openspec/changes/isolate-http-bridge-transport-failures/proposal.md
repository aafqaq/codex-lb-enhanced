# Change: Isolate HTTP bridge transport failures from account health

## Why

An HTTP-to-WebSocket bridge can lose its upstream socket after a request was
dispatched without receiving a peer-authored application error. Today, some of
those anonymous disconnects are counted as account failures. Repeated failures
from one poisoned continuity anchor can therefore drain otherwise usable
accounts one after another while the anchor itself remains the real failure
source.

## What Changes

- Treat frame-less WebSocket disconnects and send-side socket failures as
  transport evidence, not account-health evidence, even after response events
  were observed.
- Keep peer-authored authentication, quota, model, policy-close, and structured
  application failures on the existing account-health paths.
- Replace the repeated eventless-disconnect account penalty with an
  owner-fenced continuity reset for the affected bridge session.
- Preserve fail-closed delivery after ambiguous dispatch. The bridge does not
  replay a non-portable request body on another account.

## Impact

- Affected code: HTTP bridge upstream relay, submit failure classification, and
  transport-close classification.
- Existing account selection, API-key reservation settlement, direct WebSocket
  handling, quota handling, and explicit upstream error handling remain intact.
- No schema migration is required.
