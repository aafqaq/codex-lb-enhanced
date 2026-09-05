## Requirement: Account health isolation
A failure while recording advisory account health MUST NOT cancel or unexpectedly terminate a downstream user session when the upstream turn has otherwise completed or remains recoverable.

### Scenario: health write failure
- WHEN account health persistence raises during request finalization
- THEN the session lifecycle completes through its existing response path
- AND the health write error is logged and isolated
