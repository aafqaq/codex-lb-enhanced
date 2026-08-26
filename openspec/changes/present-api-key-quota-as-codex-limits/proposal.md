# Change: Present API-key quota as native Codex limits

## Why

Codex clients understand official `x-codex-*` rate-limit metadata, while
Codex LB API keys can enforce independent credit, token, or cost budgets.  The
proxy currently reports pooled upstream-account limits even when the caller's
API key has a stricter custom budget, so the desktop client displays the wrong
allowance.

## What Changes

- Map a caller API key's global custom limits to native Codex primary,
  secondary, monthly, and credit metadata.
- Prefer credits, then total tokens, cost, input tokens, and output tokens when
  more than one global limit targets the same window.
- Map 5-hour/daily limits to primary and 7-day/weekly limits to secondary.
- Fall back to the existing pooled-account estimate when the key has no custom
  global limits.
- Exclude the current request's temporary reservation from response-header
  percentages so merely starting a request does not display a false spike.

## Impact

- Affected code: Codex usage payload generation and Responses response headers.
- Existing API-key enforcement remains authoritative and unchanged.
- Model-specific limits continue to be enforced but are not represented as the
  single global Codex client allowance.
- No database migration is required.
