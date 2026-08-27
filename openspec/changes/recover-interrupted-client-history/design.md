# Design

## Recovery authority

The client's full local transcript is the only source that can survive an upstream account boundary without relying on an account-scoped response identifier. A full resend is authoritative only after the existing retained-prefix proof, deterministic account-neutral projection, and direct tool-call/output validation succeed. Interrupted assistant commentary is a valid retained boundary when it is completed, contains portable output, has no pending tool call, and the new user/developer messages form one account-neutral client turn. Codex's harmless `create_time` and `content_item_kinds` turn metadata is accepted for classification and reduced to the stable `turn_id` before cross-account dispatch.

## Anchor precedence

A proxy-injected anchor is an optimization, not a stronger source of truth than a proven full resend. The bridge may use the anchor for the first attempt on its owner, but it must retain the projected unanchored request as the failover body. Once the anchor is rejected or its owner reports quota exhaustion, the request excludes that account, clears affinity, and resumes through the ordinary load balancer with the full projected input. A later client retry carrying the same full transcript must not have the invalid anchor injected again.

## Partial output

Before visible model output, the bridge can safely retry the same logical request on another account. After visible output, server-side replay could duplicate text or tool side effects, so the bridge ends the attempt with the retryable protocol semantics expected by the client. Codex then rebuilds the turn from local history. The next full-history request is accepted unanchored. Other surfaces receive their native retryable error envelope without changing the internal routing rules.

## Safety boundaries

Cross-account replay remains unavailable for unmatched or pending tool calls, opaque file/container/vector identifiers, encrypted or hosted state that cannot be projected, malformed metadata, unknown input/tool shapes, and any request whose retained prefix cannot be proven. Pool-level quota is returned only after every eligible account allowed by the configured routing policy has been attempted or excluded.
