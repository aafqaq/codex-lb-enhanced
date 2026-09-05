## Requirement: Root Responses aliases
The service MUST accept POST `/responses` and `/responses/compact` plus trailing-slash variants and route them through the existing OpenAI-compatible Responses handlers. WebSocket `/responses` MUST be accepted through the same compatibility surface. These aliases MUST preserve authentication, validation, streaming, and error envelopes and MUST NOT return the SPA fallback 405.

### Scenario: latest Codex root Responses request
- WHEN a Codex client sends POST `/responses`
- THEN the request is handled as an OpenAI-compatible Responses request
- AND the response is not a method-not-allowed SPA fallback
