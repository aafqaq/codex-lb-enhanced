## 1. Implementation

- [x] 1.1 Centralize the durable recovery eligibility proof.
- [x] 1.2 Mark errors raised during local recovery admission and streaming.
- [x] 1.3 Preserve the existing predecessor, durable owner, and operation fence.

## 2. Regression coverage

- [x] 2.1 Cover every missing durable-fence component.
- [x] 2.2 Drive an HTTP bridge through `previous_response_not_found`, local
  recovery, and a second eventless `stream_incomplete` failure.
- [x] 2.3 Assert the nested failure is eligible for API-level indefinite
  recovery without changing fresh-turn behavior.

## 3. Validation

- [x] 3.1 Run the focused HTTP bridge unit tests.
- [x] 3.2 Run strict OpenSpec validation.
- [ ] 3.3 Verify the enhanced container health check and image revision after
  deployment.
