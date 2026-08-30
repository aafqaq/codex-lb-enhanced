# Proposal: migrate the OpenAI request core to a Sub2API-style failover loop

## Problem

The current proxy distributes account selection, continuity ownership, WebSocket
forwarding, HTTP bridge recovery, and quota handling across several independent
retry paths. A failed account can therefore remain a hard continuity owner and
prevent a healthy account from being selected. The client then receives an
owner-unavailable or stream-disconnected error even though the account pool has
capacity.

## Scope

This change introduces one request-scoped OpenAI failover controller modeled on
Sub2API's `failedAccountIDs` loop. It owns only request recovery state; the
configured normal routing strategy remains the source of account ordering.

The dashboard, account management, API-key management, reports, usage
projection, quota presentation, and non-OpenAI protocol adapters remain
unchanged. Existing account credentials and routing configuration are reused by
the new controller.

## Non-goals

- Making an upstream `previous_response_id` portable between provider accounts.
- Replacing the database account model or dashboard contracts.
- Removing support for HTTP, SSE, or Responses WebSocket transports.
- Adding a new client-specific routing policy.

## Compatibility principle

Recovery is protocol-neutral. A failure is first classified as a failure of the
selected account. The controller may select another eligible account only when
the canonical request can be replayed safely. It must never truncate the
conversation to make replay appear safe.
