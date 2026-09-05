# Design

Add canonical middleware aliases for root `/responses` and `/responses/compact` (including trailing slash and WebSocket) to the existing OpenAI-compatible `/v1` routes. Keep request handling in the existing route implementation.

Expose explicit refresh actions for settings-owned queries and use stable query invalidation/refetch behavior so buttons remain actionable after stale-data failures. Make settings cards use a responsive single-column baseline with bounded two-column layout only at wide widths.

Ensure account health persistence failures are isolated from the request/session lifecycle and do not cancel an otherwise valid downstream turn.
